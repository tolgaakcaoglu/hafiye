# Bundled wake-word models

`hafiye.onnx` — the on-device Turkish "Hafiye" hotword model. This is the
default detector for the wake word feature (see
`website/docs/user-guide/features/wake-word.md`); no training or setup is
required to say "Hafiye".

- **Engine:** [openWakeWord](https://github.com/dscripka/openWakeWord) (Apache-2.0).
- **Provenance:** trained with the official openWakeWord `train.Model` DNN
  classifier using Turkish Piper synthetic speech, generated negative speech,
  and the reproducible `scripts/train_hafiye_wakeword.py` command. The training
  source checkout is recorded in `UPSTREAM.md`.
- **Label:** the model registers as `hafiye` (matches the filename).
- **Runtime:** openWakeWord's shared feature-extraction models (melspectrogram +
  embedding) are NOT bundled here — they are fetched once on first use by
  `tools/wake_word.py` via `openwakeword.utils.download_models()`.

The historical `hey_hermes` assets remain in this directory only for upstream
compatibility. Hafiye's default config and runtime aliases resolve to
`hafiye.onnx`; the final product does not require the Hermes phrase.

To use a different phrase, train your own model and point
`wake_word.openwakeword.model` at its path, or set a built-in openWakeWord name
(`hey_jarvis`, `alexa`, `hey_mycroft`, …). See the wake-word docs and the
training script for the prescribed local workflow.
