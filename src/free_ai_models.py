"""
Free AI Models - Tích hợp Gemini và Groq API miễn phí
"""

import os
import json
import aiohttp
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def analyze(self, prompt: str) -> str:
        pass

class GeminiProvider(AIProvider):
    """Google Gemini API (Free tier)"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    async def analyze(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY không được cấu hình")
        
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    error = await response.text()
                    raise Exception(f"Gemini API error: {error}")

class GroqProvider(AIProvider):
    """Groq API (Free tier - rất nhanh)"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-70b-versatile"  # hoặc mixtral-8x7b-32768
    
    async def analyze(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY không được cấu hình")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Bạn là chuyên gia phân tích thị trường crypto. Trả lời bằng JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error = await response.text()
                    raise Exception(f"Groq API error: {error}")

class FreeAIModels:
    """Manager cho các AI providers miễn phí"""
    
    def __init__(self, provider: str = "gemini"):
        self.provider_name = provider
        self.provider = self._get_provider(provider)
    
    def _get_provider(self, name: str) -> AIProvider:
        providers = {
            "gemini": GeminiProvider,
            "groq": GroqProvider
        }
        if name not in providers:
            raise ValueError(f"Provider không hỗ trợ: {name}. Chọn: {list(providers.keys())}")
        return providers[name]()
    
    async def analyze_market(self, market_data: dict) -> dict:
        """Phân tích thị trường bằng AI"""
        prompt = self._build_analysis_prompt(market_data)
        
        try:
            response = await self.provider.analyze(prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"⚠️ AI Analysis error: {e}")
            return {"signal": "HOLD", "confidence": 0, "reason": str(e)}
    
    def _build_analysis_prompt(self, data: dict) -> str:
        return f"""
Phân tích dữ liệu thị trường crypto sau và đưa ra tín hiệu giao dịch:

Symbol: {data.get('symbol')}
Giá hiện tại: ${data.get('price')}

Chỉ báo kỹ thuật:
{json.dumps(data.get('indicators', {}), indent=2)}

20 nến gần nhất (OHLCV):
{json.dumps(data.get('klines', [])[-5:], indent=2)}

Order Book (top 5):
- Bids: {data.get('order_book', {}).get('bids', [])}
- Asks: {data.get('order_book', {}).get('asks', [])}

Volume 24h: {data.get('volume_24h')}

Trả lời CHÍNH XÁC theo format JSON sau:
{{
    "signal": "BUY" hoặc "SELL" hoặc "HOLD",
    "confidence": số từ 0 đến 1 (ví dụ: 0.85),
    "reason": "giải thích ngắn gọn",
    "support": giá hỗ trợ,
    "resistance": giá kháng cự,
    "stop_loss": giá cắt lỗ đề xuất,
    "take_profit": giá chốt lời đề xuất
}}
"""
    
    def _parse_response(self, response: str) -> dict:
        """Parse JSON response từ AI"""
        try:
            # Tìm JSON trong response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback nếu không parse được
        return {
            "signal": "HOLD",
            "confidence": 0,
            "reason": "Không thể parse response từ AI"
        }
