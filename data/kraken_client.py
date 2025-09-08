"""
Kraken public data client (stub).

Later:
- get_eur_pairs()
- get_ohlc(pair, timeframe, since=None, limit=N)

Use only public endpoints; no private/live trading.
"""
from typing import List, Any

class KrakenClient:
    def __init__(self, session=None) -> None:
        self.session = session  # requests.Session in later steps

    def get_eur_pairs(self) -> List[str]:
        """Return list of EUR-quoted pairs (stub)."""
        return ["BTC/EUR"]  # placeholder

    def get_ohlc(self, pair: str, timeframe: str, limit: int = 200) -> List[Any]:
        """Return recent OHLC candles for the pair/timeframe (stub)."""
        return []
