"""
Trading Bot Core Logic
"""

import asyncio
import random
from binance.client import Client
from binance.enums import *
from data_loader import DataLoader
from free_ai_models import FreeAIModels

class TradingBot:
    def __init__(self, api_key: str, secret_key: str, symbol: str = "BTCUSDT", 
                 ai_provider: str = "gemini", demo_mode: bool = False):
        self.symbol = symbol
        self.ai_provider = ai_provider
        self.demo_mode = demo_mode
        self.position = None
        self.running = False
        self.demo_balance = {"USDT": 10000.0, "BTC": 0.0}  # Demo balance
        
        if demo_mode:
            self.client = None
            self.data_loader = None
        else:
            self.client = Client(api_key, secret_key)
            self.data_loader = DataLoader(self.client)
        
        self.ai = FreeAIModels(provider=ai_provider)
        
    async def run(self):
        """Main trading loop"""
        self.running = True
        mode = "🎮 DEMO" if self.demo_mode else "💰 LIVE"
        print(f"{mode} - Bot đang chạy... (Ctrl+C để dừng)")
        
        cycle = 0
        while self.running:
            try:
                cycle += 1
                print(f"\n{'='*40}")
                print(f"📍 Cycle #{cycle}")
                
                # 1. Lấy dữ liệu thị trường
                if self.demo_mode:
                    market_data = self.get_demo_market_data()
                else:
                    market_data = await self.data_loader.get_market_data(self.symbol)
                
                # 2. Phân tích bằng AI
                print("🤖 Đang phân tích bằng AI...")
                analysis = await self.ai.analyze_market(market_data)
                
                # 3. Đưa ra quyết định
                decision = self.make_decision(analysis)
                
                # 4. Thực hiện giao dịch
                if decision["action"] != "HOLD":
                    if self.demo_mode:
                        self.execute_demo_trade(decision, market_data["price"])
                    else:
                        await self.execute_trade(decision)
                
                # 5. Log trạng thái
                self.log_status(market_data, analysis, decision)
                
                # Chờ trước khi lặp tiếp
                wait_time = 30 if self.demo_mode else 60
                print(f"\n⏳ Chờ {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                print("\n⏹️ Dừng bot...")
                self.running = False
            except Exception as e:
                print(f"⚠️ Lỗi: {e}")
                await asyncio.sleep(10)
    
    def get_demo_market_data(self) -> dict:
        """Tạo dữ liệu demo giả lập"""
        # Giá BTC dao động ngẫu nhiên
        base_price = 43000 + random.uniform(-2000, 2000)
        
        return {
            "symbol": self.symbol,
            "price": round(base_price, 2),
            "indicators": {
                "rsi": round(random.uniform(25, 75), 2),
                "macd": round(random.uniform(-500, 500), 2),
                "sma_20": round(base_price * 0.99, 2),
                "sma_50": round(base_price * 0.98, 2),
                "ema_12": round(base_price * 1.001, 2),
                "ema_26": round(base_price * 0.999, 2),
                "bb_upper": round(base_price * 1.03, 2),
                "bb_middle": round(base_price, 2),
                "bb_lower": round(base_price * 0.97, 2)
            },
            "klines": [{"close": round(base_price + random.uniform(-100, 100), 2)} for _ in range(5)],
            "order_book": {
                "bids": [[str(round(base_price - 10, 2)), "1.5"]],
                "asks": [[str(round(base_price + 10, 2)), "2.0"]]
            },
            "volume_24h": round(random.uniform(20000, 50000), 2)
        }
    
    def execute_demo_trade(self, decision: dict, price: float):
        """Thực hiện giao dịch demo"""
        action = decision["action"]
        
        if action == "BUY" and self.demo_balance["USDT"] > 100:
            # Mua BTC
            amount_usdt = self.demo_balance["USDT"] * 0.95
            btc_amount = amount_usdt / price
            self.demo_balance["USDT"] -= amount_usdt
            self.demo_balance["BTC"] += btc_amount
            self.position = {"side": "LONG", "entry_price": price}
            print(f"✅ [DEMO] BUY {btc_amount:.6f} BTC @ ${price:.2f}")
            
        elif action == "SELL" and self.demo_balance["BTC"] > 0:
            # Bán BTC
            btc_amount = self.demo_balance["BTC"]
            usdt_amount = btc_amount * price
            self.demo_balance["BTC"] = 0
            self.demo_balance["USDT"] += usdt_amount
            
            # Tính P/L
            if self.position:
                pnl = ((price - self.position["entry_price"]) / self.position["entry_price"]) * 100
                print(f"✅ [DEMO] SELL {btc_amount:.6f} BTC @ ${price:.2f} | P/L: {pnl:+.2f}%")
            self.position = None
    
    def make_decision(self, analysis: dict) -> dict:
        """Đưa ra quyết định giao dịch dựa trên phân tích AI"""
        signal = analysis.get("signal", "HOLD")
        confidence = analysis.get("confidence", 0)
        
        # Chỉ giao dịch khi confidence > 70%
        if confidence < 0.7:
            return {"action": "HOLD", "reason": "Confidence thấp"}
        
        if signal == "BUY" and self.position is None:
            return {"action": "BUY", "reason": analysis.get("reason", "")}
        elif signal == "SELL" and self.position is not None:
            return {"action": "SELL", "reason": analysis.get("reason", "")}
        
        return {"action": "HOLD", "reason": "Không có tín hiệu rõ ràng"}
    
    async def execute_trade(self, decision: dict):
        """Thực hiện giao dịch"""
        action = decision["action"]
        
        try:
            if action == "BUY":
                # Lấy balance USDT
                balance = self.client.get_asset_balance(asset='USDT')
                usdt_balance = float(balance['free'])
                
                # Sử dụng 95% balance
                quantity = self.calculate_quantity(usdt_balance * 0.95)
                
                if quantity > 0:
                    order = self.client.create_order(
                        symbol=self.symbol,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity
                    )
                    self.position = {"side": "LONG", "entry_price": float(order['fills'][0]['price'])}
                    print(f"✅ BUY {quantity} {self.symbol}")
                    
            elif action == "SELL":
                # Lấy balance của coin
                base_asset = self.symbol.replace("USDT", "")
                balance = self.client.get_asset_balance(asset=base_asset)
                quantity = float(balance['free'])
                
                if quantity > 0:
                    order = self.client.create_order(
                        symbol=self.symbol,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantity
                    )
                    self.position = None
                    print(f"✅ SELL {quantity} {self.symbol}")
                    
        except Exception as e:
            print(f"❌ Lỗi giao dịch: {e}")
    
    def calculate_quantity(self, usdt_amount: float) -> float:
        """Tính số lượng coin có thể mua"""
        ticker = self.client.get_symbol_ticker(symbol=self.symbol)
        price = float(ticker['price'])
        quantity = usdt_amount / price
        
        # Làm tròn theo quy định của Binance
        info = self.client.get_symbol_info(self.symbol)
        step_size = float([f for f in info['filters'] if f['filterType'] == 'LOT_SIZE'][0]['stepSize'])
        precision = len(str(step_size).split('.')[-1].rstrip('0'))
        
        return round(quantity, precision)
    
    def log_status(self, market_data: dict, analysis: dict, decision: dict):
        """Log trạng thái hiện tại"""
        print(f"\n📈 {self.symbol}: ${market_data.get('price', 'N/A')}")
        
        # Indicators
        ind = market_data.get('indicators', {})
        print(f"📊 RSI: {ind.get('rsi', 'N/A')} | MACD: {ind.get('macd', 'N/A')}")
        
        # AI Analysis
        signal = analysis.get('signal', 'N/A')
        confidence = analysis.get('confidence', 0)
        signal_emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
        print(f"🤖 AI: {signal_emoji} {signal} ({confidence*100:.1f}%)")
        print(f"   Reason: {analysis.get('reason', 'N/A')[:60]}")
        
        # Decision
        print(f"📋 Decision: {decision['action']}")
        
        # Position & Balance
        if self.demo_mode:
            print(f"💰 Balance: ${self.demo_balance['USDT']:.2f} USDT | {self.demo_balance['BTC']:.6f} BTC")
        
        if self.position:
            print(f"💼 Position: {self.position['side']} @ ${self.position['entry_price']:.2f}")
    
    def stop(self):
        """Dừng bot"""
        self.running = False
        print("🔴 Bot đang dừng...")
