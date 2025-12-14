"""
Data Loader - Lấy dữ liệu từ Binance
"""

import pandas as pd
from binance.client import Client

class DataLoader:
    def __init__(self, client: Client):
        self.client = client
    
    async def get_market_data(self, symbol: str, interval: str = "1h", limit: int = 100) -> dict:
        """Lấy dữ liệu thị trường"""
        try:
            # Lấy giá hiện tại
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            # Lấy klines (candlestick)
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = self.klines_to_dataframe(klines)
            
            # Tính các chỉ báo kỹ thuật
            indicators = self.calculate_indicators(df)
            
            # Lấy order book
            depth = self.client.get_order_book(symbol=symbol, limit=10)
            
            return {
                "symbol": symbol,
                "price": current_price,
                "klines": df.to_dict('records')[-20:],  # 20 nến gần nhất
                "indicators": indicators,
                "order_book": {
                    "bids": depth['bids'][:5],
                    "asks": depth['asks'][:5]
                },
                "volume_24h": float(self.client.get_ticker(symbol=symbol)['volume'])
            }
            
        except Exception as e:
            print(f"❌ Lỗi lấy dữ liệu: {e}")
            return {"symbol": symbol, "price": 0, "error": str(e)}
    
    def klines_to_dataframe(self, klines: list) -> pd.DataFrame:
        """Chuyển klines thành DataFrame"""
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> dict:
        """Tính các chỉ báo kỹ thuật"""
        close = df['close']
        
        # SMA
        sma_20 = close.rolling(window=20).mean().iloc[-1]
        sma_50 = close.rolling(window=50).mean().iloc[-1]
        
        # EMA
        ema_12 = close.ewm(span=12).mean().iloc[-1]
        ema_26 = close.ewm(span=26).mean().iloc[-1]
        
        # MACD
        macd = ema_12 - ema_26
        signal = close.ewm(span=9).mean().iloc[-1]
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # Bollinger Bands
        bb_middle = sma_20
        bb_std = close.rolling(window=20).std().iloc[-1]
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        return {
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "ema_12": round(ema_12, 2),
            "ema_26": round(ema_26, 2),
            "macd": round(macd, 4),
            "rsi": round(rsi, 2),
            "bb_upper": round(bb_upper, 2),
            "bb_middle": round(bb_middle, 2),
            "bb_lower": round(bb_lower, 2)
        }
    
    async def get_historical_data(self, symbol: str, interval: str = "1d", days: int = 30) -> pd.DataFrame:
        """Lấy dữ liệu lịch sử"""
        klines = self.client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=f"{days} days ago UTC"
        )
        return self.klines_to_dataframe(klines)
