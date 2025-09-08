from utils.logging import get_logger

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
