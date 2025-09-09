from utils.logging import get_logger
from data.kraken_client import KrakenClient

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
        candles = kc.get_ohlc(pair=pair, timeframe=timeframe, limit=5)
        if candles:
            last = candles[-1]
            LOG.info("Fetched %d candles for %s %s. Last close=%.2f t=%s",
                     len(candles), pair, timeframe, last["c"], last["t"])
        else:
            LOG.warning("No candles returned for %s %s", pair, timeframe)
    except Exception as e:
        LOG.warning("Data fetch demo failed: %s", e)
