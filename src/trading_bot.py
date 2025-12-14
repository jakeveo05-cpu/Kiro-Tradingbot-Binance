"""
Trading Bot Core Logic
"""

import asyncio
from binance.client import Client
from binance.enums import *
from data_loader import DataLoader
from free_ai_models import FreeAIModels

class TradingBot:
    def __init__(self, api_key: str, secret_key: str, symbol: str = "BTCUSDT", ai_provider: str = "gemini"):
        self.client = Client(api_key, secret_key)
        self.symbol = symbol
        self.ai_provider = ai_provider
        self.data_loader = DataLoader(self.client)
        self.ai = FreeAIModels(provider=ai_provider)
        self.position = None
        self.running = False
        
    async def run(self):
        """Main trading loop"""
        self.running = True
        print("🟢 Bot đang chạy...")
        
        while self.running:
            try:
                # 1. Lấy dữ liệu thị trường
                market_data = await self.data_loader.get_market_data(self.symbol)
                
                # 2. Phân tích bằng AI
                analysis = await self.ai.analyze_market(market_data)
                
                # 3. Đưa ra quyết định
                decision = self.make_decision(analysis)
                
                # 4. Thực hiện giao dịch
                if decision["action"] != "HOLD":
                    await self.execute_trade(decision)
                
                # 5. Log trạng thái
                self.log_status(market_data, analysis, decision)
                
                # Chờ trước khi lặp tiếp
                await asyncio.sleep(60)  # 1 phút
                
            except Exception as e:
                print(f"⚠️ Lỗi trong vòng lặp: {e}")
                await asyncio.sleep(30)
    
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
        print(f"🤖 AI Signal: {analysis.get('signal', 'N/A')} ({analysis.get('confidence', 0)*100:.1f}%)")
        print(f"📋 Decision: {decision['action']} - {decision.get('reason', '')}")
        print(f"💼 Position: {self.position if self.position else 'None'}")
        print("-" * 40)
    
    def stop(self):
        """Dừng bot"""
        self.running = False
        print("🔴 Bot đang dừng...")
