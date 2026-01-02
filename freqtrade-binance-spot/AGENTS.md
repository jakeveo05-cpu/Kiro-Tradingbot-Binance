# Agent Guidelines (Freqtrade Binance Spot)

This directory is a Freqtrade **user_data/config** skeleton for Binance spot (paper → live).

## Scope
- Keep changes inside `projects/freqtrade-binance-spot/`.
- Do not modify upstream Freqtrade source code.

## Safety
- Never add or expose API keys/secrets. Do not commit `config.json`.
- Default to paper/dry-run; only enable live trading when explicitly requested.

## Strategy Quality
- Avoid lookahead bias; use `informative_pairs` + `merge_informative_pair` for higher timeframes.
- Keep strategy logic deterministic and vectorized (no per-row loops unless unavoidable).
- If changing timeframes, update `config.*.example.json`, strategy `timeframe`, and `README.md`.

## Quick checks
- JSON configs should remain valid (`python3 -m json.tool ...`).

