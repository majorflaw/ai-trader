# API_CONTRACTS

## LLM ACTION CONTRACT (strict)
**Input (to LLM):** JSON of:
- indicators (rsi, ema12, ema26, ema_cross, atr, vwap, price, timeframe)
- position state (flat/long/short, size, entry_price, stop, take_profit)
- risk limits (per_trade_loss_cap, daily_loss_cap, fee_bps)

**Output (from LLM):** MUST be valid JSON:
```json
{
  "action": "enter_long" | "exit_long" | "enter_short" | "exit_short" | "hold",
  "size_fraction": 0.0,
  "stop": null,
  "take_profit": null,
  "confidence": 0.0,
  "reason": "one sentence"
}
```

## Constraints:

- `size_fraction` ∈ [0, 1].
- `confidence` ∈ [0, 1].
- `stop/take_profit` can be `null` or numeric price.

## Broker Interface (paper)

- `submit(action, size_fraction, price, stop, take_profit)` → fill simulation, fees, update PnL/state.
- Strictly no live orders.

## Data Interface

- `get_eur_pairs()` → list of tradable EUR pairs.
- `get_ohlc(pair, timeframe, since=None, limit=N)` → list of candles.

## Risk Interface

- `check_and_gate(action, price, state)` → may downgrade to hold if caps tripped.