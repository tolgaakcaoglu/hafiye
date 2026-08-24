from __future__ import annotations

from pathlib import Path

from hermes_cli import voice_runtime
from tools import transcription_tools, tts_tool


def test_managed_whisper_command_wins_over_faster_whisper(monkeypatch):
    monkeypatch.setattr(transcription_tools, "_has_managed_whisper_runtime", lambda config: True)
    monkeypatch.setattr(transcription_tools, "_HAS_FASTER_WHISPER", True)

    assert transcription_tools._get_provider({"provider": "local", "local": {"model": "base"}}) == "local_command"


def test_managed_whisper_command_template_is_used(monkeypatch):
    monkeypatch.delenv(transcription_tools.LOCAL_STT_COMMAND_ENV, raising=False)
    monkeypatch.setattr(voice_runtime, "whisper_runtime_ready", lambda **kwargs: True)

    command = transcription_tools._get_local_command_template()

    assert command is not None
    assert "hermes_cli.voice_runtime stt" in command
    assert "{input_path}" in command
    assert "{output_dir}" in command


def test_managed_piper_does_not_import_piper_into_hermes(monkeypatch, tmp_path: Path):
    called = {}

    def fake_synthesize(text, output_path, config):
        called.update({"text": text, "output_path": output_path, "config": config})
        return output_path

    monkeypatch.setattr(voice_runtime, "synthesize_piper", fake_synthesize)
    monkeypatch.setattr(tts_tool, "_import_piper", lambda: (_ for _ in ()).throw(AssertionError("imported Piper")))

    output = str(tmp_path / "reply.wav")
    result = tts_tool._generate_piper_tts(
        "Merhaba",
        output,
        {"piper": {"runtime": "managed", "voice": "tr_TR-dfki-medium"}},
    )

    assert result == output
    assert called["text"] == "Merhaba"
    assert called["config"]["piper"]["runtime"] == "managed"
