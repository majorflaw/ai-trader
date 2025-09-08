"""
Paper broker (stub). Maintains in-memory position snapshot; later persisted.
"""
from typing import Dict, Any

class PaperBroker:
    def __init__(self, fee_bps: float = 5.0) -> None:
        self.fee_bps = float(fee_bps)
        self.position = {
            "side": "flat",
            "size": 0.0,
            "entry_price": None,
            "stop": None,
            "take_profit": None,
        }

    def submit(self, action: str, size_fraction: float, price: float, stop=None, take_profit=None) -> Dict[str, Any]:
        """
        Placeholder: records intent; no PnL math yet.
        """
        return {
            "filled": True,
            "action": action,
            "size_fraction": size_fraction,
            "price": price,
            "fee_bps": self.fee_bps,
            "stop": stop,
            "take_profit": take_profit,
        }
