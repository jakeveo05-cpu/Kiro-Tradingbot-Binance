"""
Kiro Trading Bot Binance - Main Entry Point
Trading bot sử dụng AI miễn phí (Gemini, Groq) để phân tích và giao dịch
"""

import os
import asyncio
from dotenv import load_dotenv
from trading_bot import TradingBot

load_dotenv()

def print_banner():
    print("=" * 50)
    print("🚀 KIRO TRADING BOT BINANCE")
    print("   Powered by Free AI (Gemini/Groq)")
    print("=" * 50)

def print_menu():
    print("\n📋 MENU:")
    print("1. Chạy Demo Mode (không cần Binance API)")
    print("2. Chạy Live Mode (cần Binance API)")
    print("3. Test AI Analysis")
    print("4. Xem cấu hình")
    print("0. Thoát")
    return input("\nChọn: ").strip()

async def run_demo_mode():
    """Chạy demo với dữ liệu giả lập"""
    print("\n🎮 DEMO MODE - Không giao dịch thật")
    bot = TradingBot(
        api_key="demo",
        secret_key="demo",
        symbol=os.getenv("TRADING_SYMBOL", "BTCUSDT"),
        ai_provider=os.getenv("AI_PROVIDER", "gemini"),
        demo_mode=True
    )
    await bot.run()

async def run_live_mode():
    """Chạy với Binance API thật"""
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_SECRET_KEY")
    
    if not binance_api_key or binance_api_key == "your_binance_api_key_here":
        print("❌ Chưa cấu hình BINANCE_API_KEY trong .env")
        return
    if not binance_secret or binance_secret == "your_binance_secret_key_here":
        print("❌ Chưa cấu hình BINANCE_SECRET_KEY trong .env")
        return
    
    print("\n💰 LIVE MODE - Giao dịch thật!")
    print("⚠️  Cảnh báo: Bot sẽ thực hiện giao dịch với tiền thật!")
    confirm = input("Xác nhận tiếp tục? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("Đã hủy.")
        return
    
    bot = TradingBot(
        api_key=binance_api_key,
        secret_key=binance_secret,
        symbol=os.getenv("TRADING_SYMBOL", "BTCUSDT"),
        ai_provider=os.getenv("AI_PROVIDER", "gemini"),
        demo_mode=False
    )
    await bot.run()

async def test_ai():
    """Test AI analysis"""
    from free_ai_models import FreeAIModels
    
    provider = os.getenv("AI_PROVIDER", "gemini")
    print(f"\n🤖 Testing {provider.upper()} AI...")
    
    ai = FreeAIModels(provider=provider)
    
    # Dữ liệu test
    test_data = {
        "symbol": "BTCUSDT",
        "price": 43500.00,
        "indicators": {
            "rsi": 45.5,
            "macd": 150.2,
            "sma_20": 43200,
            "sma_50": 42800,
            "bb_upper": 44500,
            "bb_lower": 42500
        },
        "klines": [{"close": 43500}],
        "order_book": {"bids": [["43490", "1.5"]], "asks": [["43510", "2.0"]]},
        "volume_24h": 25000
    }
    
    try:
        result = await ai.analyze_market(test_data)
        print("\n✅ AI Response:")
        print(f"   Signal: {result.get('signal', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0)*100:.1f}%")
        print(f"   Reason: {result.get('reason', 'N/A')}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def show_config():
    """Hiển thị cấu hình hiện tại"""
    print("\n⚙️  CẤU HÌNH HIỆN TẠI:")
    print("-" * 40)
    
    binance_key = os.getenv("BINANCE_API_KEY", "")
    binance_configured = binance_key and binance_key != "your_binance_api_key_here"
    
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_configured = gemini_key and gemini_key != "your_gemini_api_key_here"
    
    groq_key = os.getenv("GROQ_API_KEY", "")
    groq_configured = groq_key and groq_key != "your_groq_api_key_here"
    
    print(f"Binance API:  {'✅ Đã cấu hình' if binance_configured else '❌ Chưa cấu hình'}")
    print(f"Gemini API:   {'✅ Đã cấu hình' if gemini_configured else '❌ Chưa cấu hình'}")
    print(f"Groq API:     {'✅ Đã cấu hình' if groq_configured else '❌ Chưa cấu hình'}")
    print(f"AI Provider:  {os.getenv('AI_PROVIDER', 'gemini')}")
    print(f"Symbol:       {os.getenv('TRADING_SYMBOL', 'BTCUSDT')}")

async def main():
    """Main function"""
    print_banner()
    
    while True:
        choice = print_menu()
        
        if choice == "1":
            await run_demo_mode()
        elif choice == "2":
            await run_live_mode()
        elif choice == "3":
            await test_ai()
        elif choice == "4":
            show_config()
        elif choice == "0":
            print("\n👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    asyncio.run(main())
