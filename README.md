# 🚀 Kiro Trading Bot Binance

Trading bot tự động sử dụng AI miễn phí (Gemini, Groq) để phân tích và giao dịch trên Binance.

## ✨ Tính năng

- 🤖 Tích hợp AI miễn phí: Google Gemini & Groq
- 📊 Phân tích kỹ thuật tự động (RSI, MACD, Bollinger Bands, SMA, EMA)
- 💹 Giao dịch tự động trên Binance
- 📈 Hỗ trợ nhiều cặp trading

## 📁 Cấu trúc

```
├── src/
│   ├── main.py           # Entry point
│   ├── trading_bot.py    # Core trading logic
│   ├── data_loader.py    # Lấy dữ liệu từ Binance
│   └── free_ai_models.py # Tích hợp Gemini & Groq
├── .env                  # API keys (không commit)
├── requirements.txt      # Dependencies
└── README.md
```

## 🛠️ Cài đặt

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/Kiro-tradingbot-Binance.git
cd Kiro-tradingbot-Binance

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài dependencies
pip install -r requirements.txt
```

## ⚙️ Cấu hình

1. Copy `.env.example` thành `.env`
2. Điền API keys:

```env
# Binance API (https://www.binance.com/en/my/settings/api-management)
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret

# Chọn AI Provider
AI_PROVIDER=gemini  # hoặc groq

# Gemini (https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_key

# Groq (https://console.groq.com/keys)
GROQ_API_KEY=your_key
```

## 🚀 Chạy Bot

```bash
cd src
python main.py
```

## ⚠️ Lưu ý

- **KHÔNG** sử dụng tiền thật khi chưa test kỹ
- Sử dụng Binance Testnet để test trước
- Bot này chỉ mang tính chất học tập và nghiên cứu
- Tác giả không chịu trách nhiệm về bất kỳ tổn thất tài chính nào

## 📝 License

MIT License
