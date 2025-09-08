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
python run.py --pair BTC/EUR --paper --dry-run
python run.py --pair BTC/EUR --paper [--timeframe 5m] [--auto-eur] [--loop-interval 15] [--dry-run]
```

`--paper` is required; the app hard-fails otherwise.
`--auto-eur` will later scan/trade all EUR-quoted pairs.
`--dry-run` runs a single lightweight cycle placeholder and exits.

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