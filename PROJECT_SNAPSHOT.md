# PROJECT_SNAPSHOT

## Files
- `run.py` — CLI entry; enforces paper-only; calls executor stub.
- `README.md` — setup and usage.
- `API_CONTRACTS.md` — LLM action contract and interfaces (initial).
- `config.example.toml` — example configuration file users can copy to `config.toml`.
- `data/kraken_client.py` — Kraken public-data client (stub).
- `indicators/indicators.py` — indicator placeholders.
- `contracts/action_contract.py` — action JSON schema + validator stub.
- `llm/groq_client.py` — Groq call wrapper (stub).
- `broker/paper_broker.py` — paper broker interface (stub).
- `risk/risk_engine.py` — risk checks (stub).
- `persistence/ledger.py` — ledger I/O (stub).
- `persistence/state.py` — state I/O (stub).
- `executor/loop.py` — main orchestration loop (stub).
- `utils/logging.py` — logging setup.
- `storage/.gitkeep` — ensure dir exists.
- `logs/.gitkeep` — ensure dir exists.
- Package `__init__.py` files.

## One-line purpose per file
- `run.py` — parse args, refuse non-paper, kick off loop.
- `README.md` — how to run.
- `API_CONTRACTS.md` — contracts spec; to be expanded.
- `config.example.toml` — shows configurable keys and typical values.
- `data/kraken_client.py` — fetch pairs/candles (to implement).
- `indicators/indicators.py` — RSI/EMA/ATR/VWAP (to implement).
- `contracts/action_contract.py` — strict JSON schema & validation.
- `llm/groq_client.py` — talk to Groq; enforce schema on output.
- `broker/paper_broker.py` — hold position & fill fees (paper).
- `risk/risk_engine.py` — enforce loss caps.
- `persistence/ledger.py` — append/read trades.
- `persistence/state.py` — persist bot state.
- `executor/loop.py` — single-cycle loop and (later) continuous loop.
- `utils/logging.py` — structured logger factory.
- `storage/.gitkeep` — placeholder.
- `logs/.gitkeep` — placeholder.

## Changes this step
- Added a validated configuration system with precedence: CLI > TOML > env > defaults. Wired into `run.py`. Added example TOML and updated docs.

## How to run (paper mode)
```bash
python run.py --paper --dry-run
```