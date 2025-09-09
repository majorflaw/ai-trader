"""
Runtime configuration loader with validation.

Precedence (highest → lowest):
1) CLI arguments (handled in run.py)
2) TOML file (default: config.toml; user can pass --config)
3) Environment variables
4) Built-in defaults (below)

No external dependencies (stdlib only).
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import os
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # Will ignore TOML if not available


_ALLOWED_TIMEFRAMES = {"1m", "5m", "15m", "1h", "4h"}


@dataclass
class Config:
    # Trading + risk
    fee_bps: float = 5.0                    # round-trip fee in basis points
    per_trade_loss_cap: float = 0.01        # max loss per trade (fraction of equity)
    daily_loss_cap: float = 0.05            # max daily loss (fraction of equity)
    timeframe: str = "5m"                   # default candle timeframe
    default_pair: str = "BTC/EUR"           # default trading pair

    # Runtime toggles
    auto_eur: bool = False                  # discover/trade EUR-quoted pairs (later step)
    loop_interval: int = 15                 # seconds between cycles (used later)

    # Integrations (public data for Kraken; Groq needs API key)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama3.1-70b"

    # Storage
    storage_dir: str = "storage"
    logs_dir: str = "logs"


def _coerce_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}


def _read_toml(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists() or p.is_dir():
        return {}
    if tomllib is None:
        return {}
    with p.open("rb") as f:
        try:
            return tomllib.load(f)
        except Exception:
            return {}


def _merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def _from_env() -> Dict[str, Any]:
    env = os.environ
    cfg: Dict[str, Any] = {}
    if "FEE_BPS" in env:
        cfg["fee_bps"] = env["FEE_BPS"]
    if "PER_TRADE_LOSS_CAP" in env:
        cfg["per_trade_loss_cap"] = env["PER_TRADE_LOSS_CAP"]
    if "DAILY_LOSS_CAP" in env:
        cfg["daily_loss_cap"] = env["DAILY_LOSS_CAP"]
    if "TIMEFRAME" in env:
        cfg["timeframe"] = env["TIMEFRAME"]
    if "DEFAULT_PAIR" in env:
        cfg["default_pair"] = env["DEFAULT_PAIR"]
    if "AUTO_EUR" in env:
        cfg["auto_eur"] = _coerce_bool(env["AUTO_EUR"])
    if "LOOP_INTERVAL" in env:
        cfg["loop_interval"] = env["LOOP_INTERVAL"]
    if "GROQ_API_KEY" in env:
        cfg["groq_api_key"] = env["GROQ_API_KEY"]
    if "GROQ_MODEL" in env:
        cfg["groq_model"] = env["GROQ_MODEL"]
    if "STORAGE_DIR" in env:
        cfg["storage_dir"] = env["STORAGE_DIR"]
    if "LOGS_DIR" in env:
        cfg["logs_dir"] = env["LOGS_DIR"]
    return cfg


def _coerce_types(raw: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = dict(raw)
    # floats
    for k in ("fee_bps", "per_trade_loss_cap", "daily_loss_cap"):
        if k in out:
            out[k] = float(out[k])
    # ints
    for k in ("loop_interval",):
        if k in out:
            out[k] = int(out[k])
    # bools
    if "auto_eur" in out:
        out["auto_eur"] = _coerce_bool(out["auto_eur"])
    # strings remain as-is
    return out


def _validate(cfg: Config) -> Config:
    if not (0.0 <= cfg.per_trade_loss_cap <= 1.0):
        raise ValueError("per_trade_loss_cap must be within [0, 1]")
    if not (0.0 <= cfg.daily_loss_cap <= 1.0):
        raise ValueError("daily_loss_cap must be within [0, 1]")
    if cfg.fee_bps < 0.0 or cfg.fee_bps > 5000.0:
        raise ValueError("fee_bps must be within [0, 5000]")
    if cfg.loop_interval <= 0:
        raise ValueError("loop_interval must be > 0")
    if cfg.timeframe not in _ALLOWED_TIMEFRAMES:
        # allow custom, but warn later; here we normalize to default
        cfg.timeframe = "5m"
    if "/" not in cfg.default_pair:
        cfg.default_pair = "BTC/EUR"
    return cfg


def load_config(toml_path: Optional[str] = "config.toml") -> Config:
    """
    Load configuration from defaults, environment, and TOML file.
    TOML (if present) overrides environment; CLI overrides both (in run.py).
    """
    defaults = asdict(Config())
    env_cfg = _from_env()
    toml_cfg = _read_toml(toml_path)
    # allow flat TOML or nested under [trading], etc. We flatten top-level only.
    # If user used a [config] table, merge it too.
    flat_toml: Dict[str, Any] = dict(toml_cfg)
    if "config" in toml_cfg and isinstance(toml_cfg["config"], dict):
        flat_toml = _merge_dict(flat_toml, toml_cfg["config"])
    merged = _merge_dict(defaults, env_cfg)
    merged = _merge_dict(merged, flat_toml)
    merged = _coerce_types(merged)
    return _validate(Config(**merged))
