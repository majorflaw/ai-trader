"""
Kraken public data client.

Endpoints:
- Asset pairs: https://api.kraken.com/0/public/AssetPairs
- OHLC:        https://api.kraken.com/0/public/OHLC

Notes:
- We normalize pair names to 'BTC/EUR' style for the user.
- Kraken prefers internal pair codes (e.g., 'XXBTZEUR'); we map both ways.
- No private endpoints are used; this project is paper-trading only.
"""
from typing import List, Any, Dict, Optional, Tuple
import json
import time
import urllib.request
import urllib.parse

_BASE_URL = "https://api.kraken.com"
_UA = "paper-bot/0.1 (+https://example.invalid)"

_TF_TO_INTERVAL = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
}

def _http_get(path: str, params: Dict[str, Any], timeout: float = 10.0, retries: int = 3, backoff: float = 0.5) -> Dict[str, Any]:
    url = f"{_BASE_URL}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    last_err: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            obj = json.loads(data.decode("utf-8"))
            if obj.get("error"):
                # Kraken returns a list of error strings; surface the first
                raise RuntimeError(f"Kraken API error: {obj['error'][0]}")
            return obj.get("result", {})
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
            else:
                raise
    # Should not reach
    if last_err:
        raise last_err
    return {}


def _normalize_wsname(wsname: str) -> str:
    # Kraken wsname is like "XBT/EUR"; map XBT->BTC for friendliness.
    if not isinstance(wsname, str):
        return "BTC/EUR"
    base, sep, quote = wsname.partition("/")
    if base == "XBT":
        base = "BTC"
    return f"{base}/{quote}" if sep else wsname


class KrakenClient:
    def __init__(self) -> None:
        self._pairs_cache: Optional[Dict[str, Dict[str, Any]]] = None  # raw AssetPairs
        # indices for quick lookup
        self._by_wsname: Dict[str, str] = {}   # "BTC/EUR" -> kraken_code
        self._by_altname: Dict[str, str] = {}  # "XBTEUR"  -> kraken_code

    # ---------- Pair metadata ----------
    def _ensure_pairs(self) -> None:
        if self._pairs_cache is not None:
            return
        res = _http_get("/0/public/AssetPairs", params={})
        # res is dict keyed by kraken pair code: e.g., "XXBTZEUR"
        self._pairs_cache = {}
        self._by_wsname.clear()
        self._by_altname.clear()
        for code, info in res.items():
            # Some pairs may be deprecated or dark; we keep those with wsname.
            wsname = info.get("wsname")
            altname = info.get("altname")
            quote = info.get("quote")
            if not wsname or not quote:
                continue
            self._pairs_cache[code] = info
            norm = _normalize_wsname(wsname)
            self._by_wsname[norm] = code
            if isinstance(altname, str):
                self._by_altname[altname] = code

    def get_eur_pairs(self) -> List[str]:
        """Return sorted list of EUR-quoted pairs in normalized form, e.g., 'BTC/EUR'."""
        self._ensure_pairs()
        assert self._pairs_cache is not None
        out: List[str] = []
        for code, info in self._pairs_cache.items():
            wsname = info.get("wsname")
            quote = info.get("quote")  # Kraken internal: 'ZEUR'
            if wsname and quote == "ZEUR":
                out.append(_normalize_wsname(wsname))
        # Unique + sorted
        return sorted(set(out))

    def _resolve_pair_code(self, user_pair: str) -> Tuple[str, str]:
        """
        Resolve a user-friendly pair like 'BTC/EUR' to Kraken's internal pair code.
        Returns (kraken_code, normalized_user_pair).
        """
        self._ensure_pairs()
        assert self._pairs_cache is not None
        # Normalize user input to Kraken's wsname style
        up = user_pair.strip().upper()
        if "/" in up:
            base, _, quote = up.partition("/")
            if base == "BTC":
                base = "XBT"  # Kraken base ticker
            norm_ws = f"{base}/{quote}"
        else:
            # Support altname like XBTEUR
            norm_ws = up

        # Direct wsname match?
        code = self._by_wsname.get(_normalize_wsname(norm_ws))
        if code:
            return code, _normalize_wsname(norm_ws)
        # altname fallback (e.g., XBTEUR)
        code = self._by_altname.get(up.replace("/", ""))
        if code:
            wsname = self._pairs_cache[code].get("wsname", "XBT/EUR")
            return code, _normalize_wsname(wsname)
        # Final attempt: scan wsname normalized values
        for wsname, c in self._by_wsname.items():
            if wsname == _normalize_wsname(norm_ws):
                return c, wsname
        raise ValueError(f"Unknown or unsupported pair: {user_pair}")

    # ---------- OHLC ----------
    def get_ohlc(self, pair: str, timeframe: str, since: Optional[int] = None, limit: int = 200) -> List[Dict[str, Any]]:
        """
        Fetch OHLC candles for `pair` and `timeframe`.
        - `pair`: user-friendly like 'BTC/EUR'
        - `timeframe`: one of {'1m','5m','15m','1h','4h'}
        - `since`: optional epoch seconds (aligns with Kraken's 'since' which expects a time index)
        - `limit`: maximum number of candles to return (slice locally)
        Returns a list of dicts: [{"t","o","h","l","c","v"}, ...] ascending by time.
        """
        if timeframe not in _TF_TO_INTERVAL:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        interval = _TF_TO_INTERVAL[timeframe]
        code, _norm = self._resolve_pair_code(pair)
        params: Dict[str, Any] = {"pair": code, "interval": interval}
        if since is not None:
            params["since"] = int(since)
        res = _http_get("/0/public/OHLC", params=params)
        # Result is { "<code>": [[time, open, high, low, close, vwap, volume, count], ...], "last": <id> }
        rows = None
        # Kraken sometimes keys by the canonical code; fetch first list-like value
        if code in res:
            rows = res.get(code, [])
        else:
            # pick first array in result
            for v in res.values():
                if isinstance(v, list):
                    rows = v
                    break
        if rows is None:
            return []
        out: List[Dict[str, Any]] = []
        for r in rows:
            # r: [time, o, h, l, c, vwap, volume, count]
            try:
                t = int(r[0])
                o = float(r[1]); h = float(r[2]); l = float(r[3]); c = float(r[4])
                v = float(r[6])  # "volume" field
                out.append({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
            except Exception:
                continue
        # Ensure ascending by time and slice to limit
        out.sort(key=lambda x: x["t"])
        if limit and len(out) > limit:
            out = out[-limit:]
        return out
