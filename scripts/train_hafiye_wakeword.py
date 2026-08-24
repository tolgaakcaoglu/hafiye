#!/usr/bin/env python3
"""Train the bundled Hafiye openWakeWord model.

This is a small, reproducible wrapper around the official openWakeWord
training model.  The training environment is intentionally separate from the
Hafiye runtime because openWakeWord's optional training stack is much larger
than its ONNX inference dependencies.

The script creates fixed 2-second, 16 kHz clips, computes the official
openWakeWord speech-embedding features, trains the official DNN classifier,
and exports ``hafiye.onnx``.  Piper is used only to create Turkish training
speech; the resulting runtime model remains the local openWakeWord ONNX
model.

Example::

    python scripts/train_hafiye_wakeword.py \
        --piper-python ~/.local/share/hafiye/runtimes/piper/venv/bin/python \
        --piper-data-dir ~/.local/share/hafiye/runtimes/piper/voices \
        --output-dir ~/.local/share/hafiye/runtimes/openwakeword-training/hafiye \
        --export tools/wakewords/hafiye.onnx

The script requires the official openWakeWord source package, PyTorch,
onnxruntime, scipy, scikit-learn, torchinfo, and torchmetrics in the training
environment.  It does not install packages itself.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
import sys
import types
import tempfile
import wave
from pathlib import Path

import numpy as np
import torch
import onnx
from scipy.signal import resample_poly

# ``openwakeword.train`` imports the optional, full augmentation pipeline at
# module import time.  The wrapper performs its own deterministic Piper/audio
# augmentation below, so load the official classifier without pulling in the
# training-only librosa/torchaudio stack (which is not Python 3.13 compatible
# on every platform).
_training_data_stub = types.ModuleType("openwakeword.data")
_training_data_stub.generate_adversarial_texts = None
_training_data_stub.augment_clips = None
_training_data_stub.mmap_batch_generator = None
sys.modules.setdefault("openwakeword.data", _training_data_stub)

from openwakeword.train import Model
from openwakeword.utils import AudioFeatures


SAMPLE_RATE = 16_000
CLIP_SAMPLES = 32_000
FEATURE_SHAPE = (16, 96)
POSITIVE_TEXTS = (
    "Hafiye",
    "Hafiye.",
    "Hafiye, dinle.",
    "Hafiye, buraya bak.",
    "Hafiye, hazır mısın?",
    "Hafiye, sana ihtiyacım var.",
    "Hafiye, lütfen cevap ver.",
    "Hafiye, şimdi dinle.",
)
NEGATIVE_TEXTS = (
    "Bugün hava nasıl?",
    "Lütfen pencereyi aç.",
    "Toplantı saat üçte başlayacak.",
    "Bana Türkçe cevap ver.",
    "Mutfakta biraz su var.",
    "Yarın erkenden yola çıkacağız.",
    "Bu dosyayı masaüstüne kaydet.",
    "Ses seviyesini biraz azalt.",
    "İstanbul'da bugün hava serin.",
    "Bilgisayarı şimdi kapatma.",
    "Kahve hazır, istersen içebilirsin.",
    "Bu akşam evde çalışacağım.",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--piper-python", type=Path, required=True)
    parser.add_argument("--piper-data-dir", type=Path, required=True)
    parser.add_argument("--piper-model", default="tr_TR-dfki-medium")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=384, help="clips per class")
    parser.add_argument("--steps", type=int, default=900)
    parser.add_argument("--seed", type=int, default=20260824)
    parser.add_argument("--cpu-threads", type=int, default=4)
    return parser.parse_args()


def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as source:
        if source.getnchannels() != 1 or source.getsampwidth() != 2:
            raise ValueError(f"Piper output must be mono 16-bit PCM: {path}")
        return np.frombuffer(source.readframes(source.getnframes()), dtype=np.int16), source.getframerate()


def _to_16k(audio: np.ndarray, sample_rate: int) -> np.ndarray:
    if sample_rate == SAMPLE_RATE:
        return audio.astype(np.float32)
    converted = resample_poly(audio.astype(np.float32), SAMPLE_RATE, sample_rate)
    return converted.astype(np.float32)


def _piper_batch(
    piper_python: Path,
    data_dir: Path,
    model: str,
    texts: tuple[str, ...],
    destination: Path,
    *,
    length_scale: float,
    noise_scale: float,
    noise_w_scale: float,
) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    text_file = destination / "input.txt"
    text_file.write_text("\n".join(texts) + "\n", encoding="utf-8")
    command = [
        str(piper_python),
        "-m",
        "piper",
        "--data-dir",
        str(data_dir),
        "-m",
        model,
        "-i",
        str(text_file),
        "-d",
        str(destination),
        "--output-dir-naming",
        "text",
        "--length-scale",
        str(length_scale),
        "--noise-scale",
        str(noise_scale),
        "--noise-w-scale",
        str(noise_w_scale),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=900)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Piper failed").strip()
        raise RuntimeError(detail[-4000:])
    files = sorted(destination.glob("*.wav"))
    if not files:
        raise RuntimeError(f"Piper created no WAV files in {destination}")
    return files


def _normalize(audio: np.ndarray, gain: float) -> np.ndarray:
    audio = audio * gain
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 31_000:
        audio *= 31_000 / peak
    return audio


def _make_clip(source: np.ndarray, rng: np.random.Generator, *, positive: bool) -> np.ndarray:
    """Place a short utterance in a varied, quiet two-second room clip."""
    source = source.astype(np.float32)
    if source.size > 19_000:
        source = source[:19_000]

    # Small time-scale changes model different speaking rates without requiring
    # a second TTS engine.  The source remains recognizably Turkish speech.
    scale = float(rng.uniform(0.88, 1.14))
    target = max(4000, int(source.size / scale))
    if target != source.size:
        source = resample_poly(source, target, source.size).astype(np.float32)
    source = source[:19_000]

    clip = rng.normal(0.0, rng.uniform(2.0, 16.0), CLIP_SAMPLES).astype(np.float32)
    if positive:
        start = int(rng.integers(4_000, max(4_001, CLIP_SAMPLES - source.size - 2_000)))
    else:
        start = int(rng.integers(3_000, max(3_001, CLIP_SAMPLES - source.size - 2_000)))
    gain = float(rng.uniform(0.72, 1.08))
    clip[start : start + source.size] += _normalize(source, gain)

    # Add a very quiet stationary room component to keep the classifier from
    # learning absolute silence as the negative class.
    room = rng.normal(0.0, rng.uniform(1.0, 7.0), CLIP_SAMPLES)
    clip += room
    return np.clip(clip, -32768, 32767).astype(np.int16)


def _make_dataset(args: argparse.Namespace, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    synthetic = args.output_dir / "synthetic"
    positive_dir = synthetic / "positive"
    negative_dir = synthetic / "negative"
    positive_files: list[Path] = []
    negative_files: list[Path] = []

    for index, length_scale in enumerate((0.86, 0.96, 1.08, 1.20)):
        positive_files.extend(
            _piper_batch(
                args.piper_python,
                args.piper_data_dir,
                args.piper_model,
                POSITIVE_TEXTS,
                positive_dir / f"batch-{index}",
                length_scale=length_scale,
                noise_scale=float(0.55 + index * 0.12),
                noise_w_scale=float(0.55 + index * 0.10),
            )
        )
        negative_files.extend(
            _piper_batch(
                args.piper_python,
                args.piper_data_dir,
                args.piper_model,
                NEGATIVE_TEXTS,
                negative_dir / f"batch-{index}",
                length_scale=length_scale,
                noise_scale=float(0.55 + index * 0.12),
                noise_w_scale=float(0.55 + index * 0.10),
            )
        )

    def load(paths: list[Path], positive: bool) -> np.ndarray:
        clips = []
        for index in range(args.samples):
            path = paths[index % len(paths)]
            audio, sample_rate = _read_wav(path)
            clips.append(_make_clip(_to_16k(audio, sample_rate), rng, positive=positive))
        return np.stack(clips)

    positives = load(positive_files, True)
    negatives = load(negative_files, False)
    return positives, negatives


def _train_model(features: np.ndarray, labels: np.ndarray, steps: int, seed: int) -> tuple[Model, dict[str, float]]:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    classifier = Model(n_classes=1, input_shape=FEATURE_SHAPE, model_type="dnn", layer_dim=32, n_blocks=1)
    device = classifier.device
    classifier.model.to(device)

    permutation = np.random.default_rng(seed).permutation(len(features))
    split = max(1, int(len(features) * 0.8))
    train_indices = permutation[:split]
    validation_indices = permutation[split:]
    if len(validation_indices) == 0:
        validation_indices = train_indices[-1:]

    x_train = torch.from_numpy(features[train_indices]).float().to(device)
    y_train = torch.from_numpy(labels[train_indices, None]).float().to(device)
    x_val = torch.from_numpy(features[validation_indices]).float().to(device)
    y_val = torch.from_numpy(labels[validation_indices, None]).float().to(device)
    optimizer = torch.optim.Adam(classifier.model.parameters(), lr=0.001)
    batch_size = min(64, len(x_train))

    classifier.model.train()
    for step in range(steps):
        indices = torch.randint(0, len(x_train), (batch_size,), device=device)
        predictions = classifier.model(x_train[indices])
        loss = torch.nn.functional.binary_cross_entropy(predictions, y_train[indices])
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if (step + 1) % max(1, steps // 5) == 0:
            print(f"training step {step + 1}/{steps}, loss={loss.item():.5f}", flush=True)

    classifier.model.eval()
    with torch.no_grad():
        validation_scores = classifier.model(x_val).squeeze(1).cpu().numpy()
    positive_scores = validation_scores[y_val.squeeze(1).cpu().numpy() == 1]
    negative_scores = validation_scores[y_val.squeeze(1).cpu().numpy() == 0]
    metrics = {
        "validation_positive_min": float(np.min(positive_scores)) if len(positive_scores) else 0.0,
        "validation_positive_mean": float(np.mean(positive_scores)) if len(positive_scores) else 0.0,
        "validation_negative_max": float(np.max(negative_scores)) if len(negative_scores) else 0.0,
        "validation_negative_mean": float(np.mean(negative_scores)) if len(negative_scores) else 0.0,
        "validation_accuracy_at_0_6": float(
            np.mean((validation_scores >= 0.6) == y_val.squeeze(1).cpu().numpy())
        ),
    }
    return classifier, metrics


def main() -> int:
    args = _parse_args()
    if args.samples < 32:
        raise SystemExit("--samples must be at least 32")
    random.seed(args.seed)
    np.random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.export.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    print(f"creating {args.samples} positive and {args.samples} negative clips", flush=True)
    positives, negatives = _make_dataset(args, rng)
    all_clips = np.concatenate([positives, negatives])
    labels = np.concatenate(
        [np.ones(len(positives), dtype=np.float32), np.zeros(len(negatives), dtype=np.float32)]
    )

    print("computing official openWakeWord features", flush=True)
    features = AudioFeatures(inference_framework="onnx", device="cpu", ncpu=args.cpu_threads).embed_clips(
        all_clips, batch_size=32, ncpu=args.cpu_threads
    )
    if features.shape[1:] != FEATURE_SHAPE:
        raise RuntimeError(f"unexpected feature shape {features.shape[1:]}; expected {FEATURE_SHAPE}")

    classifier, metrics = _train_model(features, labels, args.steps, args.seed)
    print(json.dumps(metrics, indent=2, sort_keys=True), flush=True)
    if metrics["validation_positive_mean"] < 0.85 or metrics["validation_negative_max"] >= 0.6:
        raise RuntimeError(f"synthetic validation did not meet the acceptance margin: {metrics}")

    temporary_export = args.output_dir / "hafiye.onnx"
    classifier.export_to_onnx(str(temporary_export), class_mapping="hafiye")
    # Newer PyTorch exporters may place the small classifier weights in an
    # adjacent ``.onnx.data`` file.  Hafiye ships one portable model asset, so
    # consolidate the external initializers before copying the artifact.
    onnx_model = onnx.load(str(temporary_export), load_external_data=True)
    onnx.save_model(onnx_model, str(temporary_export), save_as_external_data=False)
    shutil.copy2(temporary_export, args.export)
    manifest = {
        "model": "hafiye",
        "phrase": "Hafiye",
        "engine": "openWakeWord",
        "inference_framework": "onnx",
        "feature_shape": list(FEATURE_SHAPE),
        "samples_per_class": args.samples,
        "training_steps": args.steps,
        "seed": args.seed,
        "piper_model": args.piper_model,
        "synthetic_validation": metrics,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"exported {args.export}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
