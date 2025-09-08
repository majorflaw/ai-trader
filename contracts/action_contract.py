"""
Strict action contract schema and validation (stub).
"""

from typing import Any, Dict

VALID_ACTIONS = {"enter_long", "exit_long", "enter_short", "exit_short", "hold"}

def empty_contract() -> Dict[str, Any]:
    return {
        "action": "hold",
        "size_fraction": 0.0,
        "stop": None,
        "take_profit": None,
        "confidence": 0.0,
        "reason": "initial placeholder",
    }

def validate_contract(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and coerce minimal fields. Full checks added later.
    """
    if not isinstance(obj, dict):
        return empty_contract()
    action = obj.get("action", "hold")
    if action not in VALID_ACTIONS:
        action = "hold"
    size = obj.get("size_fraction", 0.0)
    try:
        size = float(size)
    except Exception:
        size = 0.0
    size = max(0.0, min(1.0, size))
    conf = obj.get("confidence", 0.0)
    try:
        conf = float(conf)
    except Exception:
        conf = 0.0
    conf = max(0.0, min(1.0, conf))
    return {
        "action": action,
        "size_fraction": size,
        "stop": obj.get("stop", None),
        "take_profit": obj.get("take_profit", None),
        "confidence": conf,
        "reason": str(obj.get("reason", "placeholder")),
    }
