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

## Quantitative risk engine extension

`voicedata.risk` implements sample annualized volatility, compounded maximum drawdown, nearest-rank historical VaR/expected shortfall (as nonnegative losses), and equal-weight returns for aligned asset series. Run `pytest -q tests/test_risk.py`. The current risk implementation is pure Python and does not require market-data or paid APIs.

It is **not yet connected to spoken intents or the SQLite analytics tools**, nor is it validated against a production portfolio engine. **Planned next:** approved risk tool schemas, point-in-time market price ingestion, covariance-based optimization, rolling backtests, and optional Black-Scholes/option volatility exercises. Short-sample historical risk estimates are unstable.
