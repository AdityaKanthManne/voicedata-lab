# VoiceData Lab — Local Analytics Copilot

A reproducible natural-language analytics prototype with a deterministic SQL engine and optional offline speech-to-text/text-to-speech adapters.

## Quick start
```bash
python -m pip install -e '.[dev]'
voicedata init --db demo.db
voicedata ask --db demo.db --text "Show revenue for DemoCo"
pytest -q
```

Uses **synthetic DemoCo** quarterly revenue values (20, 24, 27, 35 million units) and calculates quarter-over-quarter growth with a parameterized SQLite query.

## Optional local speech
```bash
python -m pip install -e '.[voice]'
voicedata voice --db demo.db --audio recording.wav
voicedata ask --db demo.db --text "Show revenue for DemoCo" --speak
```

The first command transcribes an existing audio file with faster-whisper (model download required). The second uses the macOS `say` command for speech output.

## Limitations
This is not yet a live microphone/WebSocket frontend, chart dashboard or general natural-language-to-SQL agent. Supports a narrow revenue-trend intent and returns structured chart-ready JSON. Accuracy and latency targets have not been measured.
