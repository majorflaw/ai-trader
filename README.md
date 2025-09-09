# Paper-Trading Agent (Kraken + Groq)

Unattended **paper**-trading bot:
- Fetches Kraken candles
- Computes RSI, EMA(12/26) cross, ATR, VWAP
- Calls a Groq LLM that returns a strict ACTION CONTRACT JSON
- Executes **paper** trades with risk caps, fees, and PnL
- Persists ledger/state and logs everything

## Status
Step 1 scaffold. Logic is stubbed; forward paper testing will come in later steps.

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
python run.py --paper --dry-run
python run.py --paper [--pair BTC/EUR] [--timeframe 5m] [--auto-eur] [--loop-interval 15] [--dry-run] [--config config.toml]
```

- `--paper` is required; the app hard-fails otherwise.
- `--auto-eur` will later scan/trade all EUR-quoted pairs.
- `--dry-run` runs a single lightweight cycle placeholder and exits.
- `--config` points to a TOML file; CLI flags override file/env.

## Configuration

The app reads configuration in this order (highest wins):
1. CLI flags
2. config.toml (or the path you pass with --config)
3. Environment variables
4. Built-in defaults

### Environment variables
- `FEE_BPS` (default `5.0`)
- `PER_TRADE_LOSS_CAP` (default `0.01`)
- `DAILY_LOSS_CAP` (default `0.05`)
- `TIMEFRAME` (default `5m`; allowed: `1m, 5m, 15m, 1h, 4h`)
- `DEFAULT_PAIR` (default `BTC/EUR`)
- `AUTO_EUR` (true/false, default `false`)
- `LOOP_INTERVAL` (seconds, default `15`)
- `GROQ_API_KEY` (optional; needed later)
- `GROQ_MODEL` (default `llama3.1-70b`)
- `STORAGE_DIR` (default `storage`)
- `LOGS_DIR` (default `logs`)

### TOML file
See `config.example.toml` for a starting point. Any of the above keys can be set at the top level or under a `[config]` table.

## Project Layout

- `data/:` Kraken API client
- `indicators/:` RSI, EMA, ATR, VWAP (stubs now)
- `contracts/:` LLM action contract schema + validators
- `llm/:` Groq client wrapper
- `broker/:` Paper broker (fees, PnL)
- `risk/:` Risk engine (daily/per-trade caps)
- `persistence/:` Ledger/state I/O
- `executor/:` Orchestration loop
- `utils/:` Logging and helpers
- `storage/:` On-disk state/ledger
- `logs/:` Rotating logs

## Safety

This project is **paper trading** only. Any attempt at live orders must raise a hard error.

## License

MIT