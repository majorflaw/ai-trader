"""
Risk engine (stub). Later enforces per-trade and daily loss caps.
"""
from typing import Dict, Any

class RiskGate:
    def __init__(self, per_trade_loss_cap: float = 0.01, daily_loss_cap: float = 0.05) -> None:
        self.per_trade_loss_cap = float(per_trade_loss_cap)
        self.daily_loss_cap = float(daily_loss_cap)

    def check_and_gate(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        For Step 1, pass-through.
        Later: downgrade actions to 'hold' when caps are tripped.
        """
        return proposal
