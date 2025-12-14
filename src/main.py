"""
Kiro Trading Bot Binance - Main Entry Point
Trading bot sử dụng AI miễn phí (Gemini, Groq) để phân tích và giao dịch
"""

import os
import asyncio
from dotenv import load_dotenv
from trading_bot import TradingBot

load_dotenv()

async def main():
    """Main function to run the trading bot"""
    print("=" * 50)
    print("🚀 KIRO TRADING BOT BINANCE")
    print("=" * 50)
    
    # Kiểm tra API keys
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_SECRET_KEY")
    
    if not binance_api_key or not binance_secret:
        print("❌ Thiếu BINANCE_API_KEY hoặc BINANCE_SECRET_KEY trong .env")
        return
    
    # Khởi tạo bot
    bot = TradingBot(
        api_key=binance_api_key,
        secret_key=binance_secret,
        symbol=os.getenv("TRADING_SYMBOL", "BTCUSDT"),
        ai_provider=os.getenv("AI_PROVIDER", "gemini")
    )
    
    print(f"📊 Symbol: {bot.symbol}")
    print(f"🤖 AI Provider: {bot.ai_provider}")
    print("-" * 50)
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n⏹️ Bot đã dừng bởi người dùng")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(main())
