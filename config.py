"""
Runtime config (stub). Will be expanded and validated later.
"""
from dataclasses import dataclass

@dataclass
class Config:
    fee_bps: float = 5.0
    per_trade_loss_cap: float = 0.01
    daily_loss_cap: float = 0.05
    timeframe: str = "5m"
    default_pair: str = "BTC/EUR"

def load_config() -> Config:
    # Later: read env / file; validate
    return Config()
