from utils.logging import get_logger
from data.kraken_client import KrakenClient
from indicators.indicators import compute_indicators

LOG = get_logger("executor.loop")

def run_single_cycle(pair: str, timeframe: str, dry_run: bool = True) -> None:
    """
    Step 1 placeholder: log a heartbeat and return.
    Later this will:
      - fetch candles
      - compute indicators
      - call LLM
      - apply risk
      - execute paper trade
      - persist
    """
    LOG.info("Heartbeat: pair=%s timeframe=%s dry_run=%s", pair, timeframe, dry_run)
    # Step 3: Demonstrate data fetch lightly in dry-run
    try:
        kc = KrakenClient()
        pairs = kc.get_eur_pairs()
        LOG.info("Discovered %d EUR pairs (sample): %s", len(pairs), ", ".join(pairs[:5]))
        # Fetch enough history for EMA26/RSI14/ATR14 to be valid
        candles = kc.get_ohlc(pair=pair, timeframe=timeframe, limit=300)
        if candles:
            last = candles[-1]
            LOG.info("Fetched %d candles for %s %s. Last close=%.2f t=%s",
                     len(candles), pair, timeframe, last["c"], last["t"])
            # Step 4: compute indicators and log a compact summary
            ind = compute_indicators(candles, timeframe)
            LOG.info(
                "Indicators: RSI=%.2f EMA12=%.2f EMA26=%.2f x=%s ATR=%.4f VWAP=%.2f",
                ind["rsi"] if ind["rsi"] is not None else float("nan"),
                ind["ema12"] if ind["ema12"] is not None else float("nan"),
                ind["ema26"] if ind["ema26"] is not None else float("nan"),
                ind["ema_cross"] if ind["ema_cross"] is not None else "none",
                ind["atr"] if ind["atr"] is not None else float("nan"),
                ind["vwap"] if ind["vwap"] is not None else float("nan"),
            )
        else:
            LOG.warning("No candles returned for %s %s", pair, timeframe)
    except Exception as e:
        LOG.warning("Data fetch demo failed: %s", e)
