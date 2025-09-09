#!/usr/bin/env python3
import argparse
import sys
from executor.loop import run_single_cycle
from utils.logging import get_logger
from config import load_config

LOG = get_logger("run")

def parse_args():
    p = argparse.ArgumentParser(description="Paper-trading agent (Kraken + Groq)")
    p.add_argument("--pair", type=str, default=None, help="Trading pair, e.g., BTC/EUR (overrides config)")
    p.add_argument("--timeframe", type=str, default=None, help="Candle timeframe (e.g., 1m, 5m, 15m) (overrides config)")
    p.add_argument("--paper", action="store_true", help="REQUIRED: enforce paper trading only")
    p.add_argument("--auto-eur", action="store_true", help="(Later) trade all EUR-quoted pairs")
    p.add_argument("--loop-interval", type=int, default=15, help="Seconds between cycles (later used)")
    p.add_argument("--dry-run", action="store_true", help="Run a single placeholder cycle and exit")
    p.add_argument("--config", type=str, default="config.toml", help="Path to TOML config file")
    return p.parse_args()

def main():
    args = parse_args()
    if not args.paper:
        LOG.error("Live trading is disabled. Pass --paper to proceed.")
        sys.exit(2)

    cfg = load_config(args.config)

    # CLI overrides config
    pair = args.pair or cfg.default_pair
    timeframe = args.timeframe or cfg.timeframe
    auto_eur = args.auto_eur or cfg.auto_eur

    LOG.info("Starting in PAPER mode.")
    LOG.info("Config loaded from %s", args.config)
    LOG.info(
        "Pair=%s timeframe=%s dry_run=%s auto_eur=%s fee_bps=%.3f per_trade_cap=%.3f daily_cap=%.3f",
        pair, timeframe, args.dry_run, auto_eur, cfg.fee_bps, cfg.per_trade_loss_cap, cfg.daily_loss_cap
    )

    # Step 1: placeholder single cycle
    run_single_cycle(pair=pair, timeframe=timeframe, dry_run=args.dry_run)

    # Later: continuous loop unless --dry-run
    if not args.dry_run:
        LOG.info("Continuous loop will be implemented in a later step.")
    LOG.info("Exit.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())