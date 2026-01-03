# Freqtrade Binance Spot (paper → live)

Repo này là skeleton `user_data/` + config mẫu để chạy Freqtrade trên Binance **spot**.

## 1) Cài Freqtrade

Làm theo upstream docs (khuyến nghị): `https://github.com/freqtrade/freqtrade` → `docs/installation.md`.

Hoặc cài nhanh bằng venv (đúng với WSL/Linux):

```bash
cd /home/tuan/projects/Kiro-tradingbot-Binance/freqtrade-binance-spot
python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/pip install "freqtrade==2025.12"
```

Chạy CLI bằng: `.venv/bin/freqtrade` (thay vì `freqtrade`).

## 2) Tạo config thật (paper)

```bash
cd /home/tuan/projects/Kiro-tradingbot-Binance/freqtrade-binance-spot
cp config.paper.example.json config.json
# paper/dry-run: có thể để trống key/secret
```

Strategy options:
- `BinanceSpotBbRsiDipStrategy` (khuyến nghị): buy dip (BB + RSI) trong uptrend EMA, filter 4h.
- `BinanceSpotEmaRsiWithHTFStrategy`: EMA+RSI cross 2h + filter xu hướng 4h.
- `BinanceSpotEmaRsiStrategy`: EMA+RSI 2h, không filter 4h (ít phụ thuộc data hơn).

## 3) Download data + backtest

```bash
.venv/bin/freqtrade download-data -c config.json --exchange binance --timeframes 2h 4h --days 365
.venv/bin/freqtrade backtesting -c config.json --enable-protections
```

## 4) Chạy paper (dry-run)

Ví dụ (sau khi đã cài freqtrade CLI):

```bash
.venv/bin/freqtrade trade -c config.json
```

## 5) Chuyển live (cẩn thận)

```bash
cp config.live.example.json config.json
# điền key/secret + kiểm tra lại stake/max_open_trades/pairs
.venv/bin/freqtrade trade -c config.json
```

## Paper → live checklist (tối thiểu)

- Binance API key: bật **Read + Trade**, tắt Withdraw, bật IP whitelist nếu có.
- Backtest nhiều giai đoạn (khác timerange) + kiểm tra slippage/fees thực tế.
- Chạy `dry_run` ít nhất 24h với đúng pairs/timeframe (chỉ khác `dry_run=true`).
- Live: bắt đầu stake nhỏ + `max_open_trades` nhỏ, theo dõi log/PNL liên tục.
