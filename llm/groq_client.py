"""
Groq LLM wrapper (stub). No network calls in Step 1.
"""
from typing import Dict, Any
from contracts.action_contract import empty_contract, validate_contract

class GroqClient:
    def __init__(self, model: str = "llama3.1-70b") -> None:
        self.model = model

    def decide(self, indicators: Dict[str, Any], position: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build input JSON and (later) call Groq.
        Step 1 returns a validated placeholder contract.
        """
        return validate_contract(empty_contract())
