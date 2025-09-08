"""
State I/O (stub). JSON later.
"""
from typing import Dict, Any

def load_state() -> Dict[str, Any]:
    return {"initialized": True}

def save_state(state: Dict[str, Any]) -> None:
    return None
