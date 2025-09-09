"""
Indicator implementations (stdlib only):
- RSI (Wilder 14)
- EMA(12) / EMA(26) and crossover detection
- ATR (Wilder 14)
- VWAP (cumulative or windowed)
"""
from typing import List, Dict, Any, Optional

# ---------- Helpers ----------
def _ema(values: List[float], period: int) -> Optional[List[float]]:
    if period <= 0 or not values or len(values) < period:
        return None
    k = 2.0 / (period + 1.0)
    out: List[float] = [0.0] * len(values)
    # seed with SMA
    sma = sum(values[:period]) / period
    out[period - 1] = sma
    for i in range(period, len(values)):
        out[i] = values[i] * k + out[i - 1] * (1.0 - k)
    return out


def _rsi(prices: List[float], period: int = 14) -> Optional[List[float]]:
    if period <= 0 or len(prices) < period + 1:
        return None
    gains: List[float] = [0.0] * len(prices)
    losses: List[float] = [0.0] * len(prices)
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        gains[i] = max(delta, 0.0)
        losses[i] = max(-delta, 0.0)
    # Wilder smoothing (EMA-like with alpha=1/period)
    avg_gain = sum(gains[1 : period + 1]) / period
    avg_loss = sum(losses[1 : period + 1]) / period
    rsis: List[Optional[float]] = [None] * len(prices)
    # First RSI at index 'period'
    rs = (avg_gain / avg_loss) if avg_loss != 0 else float("inf")
    rsis[period] = 100.0 - (100.0 / (1.0 + rs))
    for i in range(period + 1, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        rs = (avg_gain / avg_loss) if avg_loss != 0 else float("inf")
        rsis[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsis


def _atr(candles: List[Dict[str, float]], period: int = 14) -> Optional[List[float]]:
    n = len(candles)
    if period <= 0 or n < period + 1:
        return None
    # True Range per bar starting from index 1 (needs previous close)
    trs: List[float] = [0.0] * n
    for i in range(1, n):
        h = candles[i]["h"]
        l = candles[i]["l"]
        pc = candles[i - 1]["c"]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs[i] = tr
    # Wilder ATR: first ATR = SMA of TR over 'period', then recursive
    atrs: List[Optional[float]] = [None] * n
    first_atr = sum(trs[1 : period + 1]) / period
    atrs[period] = first_atr
    for i in range(period + 1, n):
        atrs[i] = (atrs[i - 1] * (period - 1) + trs[i]) / period  # type: ignore
    # replace None with 0.0 for indices before 'period' (not used)
    return [a if a is not None else 0.0 for a in atrs]  # type: ignore


def _vwap(candles: List[Dict[str, float]], window: Optional[int] = None) -> Optional[float]:
    if not candles:
        return None
    data = candles[-window:] if (window and window > 0) else candles
    num = 0.0
    den = 0.0
    for r in data:
        tp = (r["h"] + r["l"] + r["c"]) / 3.0
        v = r["v"]
        num += tp * v
        den += v
    if den == 0.0:
        return None
    return num / den


# ---------- Public API ----------
def compute_indicators(candles: List[Dict[str, Any]], timeframe: str) -> Dict[str, Any]:
    """
    Expect candles like: [{"t": epoch_sec, "o": ..., "h": ..., "l": ..., "c": ..., "v": ...}, ...]
    Returns a dict with keys: rsi, ema12, ema26, ema_cross, atr, vwap, price, timeframe.
    All values are floats where available; otherwise None if insufficient data.
    """
    out = {
        "rsi": None,
        "ema12": None,
        "ema26": None,
        "ema_cross": None,   # 'bull', 'bear', 'bull_cross', 'bear_cross', or None
        "atr": None,
        "vwap": None,
        "price": candles[-1]["c"] if candles else None,
        "timeframe": timeframe,
    }
    if not candles or len(candles) < 2:
        return out

    closes = [float(r["c"]) for r in candles]
    ema12_series = _ema(closes, 12)
    ema26_series = _ema(closes, 26)
    rsi_series = _rsi(closes, 14)
    atr_series = _atr(candles, 14)
    vwap_val = _vwap(candles)  # cumulative

    # Fill current values if available
    if ema12_series:
        out["ema12"] = ema12_series[-1]
    if ema26_series:
        out["ema26"] = ema26_series[-1]
    if rsi_series:
        # last non-None
        for v in reversed(rsi_series):
            if v is not None:
                out["rsi"] = v
                break
    if atr_series:
        out["atr"] = atr_series[-1]
    out["vwap"] = vwap_val

    # Crossover detection
    if ema12_series and ema26_series and len(ema26_series) == len(ema12_series):
        e12_now = ema12_series[-1]
        e26_now = ema26_series[-1]
        regime = "bull" if e12_now > e26_now else ("bear" if e12_now < e26_now else "none")
        label = regime
        # fresh cross if previous regime differs
        prev_e12 = ema12_series[-2]
        prev_e26 = ema26_series[-2]
        prev_regime = "bull" if prev_e12 > prev_e26 else ("bear" if prev_e12 < prev_e26 else "none")
        if regime != "none" and prev_regime != "none" and regime != prev_regime:
            label = "bull_cross" if regime == "bull" else "bear_cross"
        out["ema_cross"] = label

    return out
