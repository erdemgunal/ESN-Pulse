"""
ESN PULSE HTTP Client

Bu modül, ESN PULSE projesinin HTTP istemcisini içerir.
"""

import asyncio
import logging
import random
from typing import Dict, List, Optional, Union

import aiohttp
from aiohttp import ClientResponse, ClientSession, ClientTimeout

from src.config import settings
from src.utils.exceptions import (
    CloudflareError,
    NetworkError,
    RateLimitError,
    TimeoutError
)

logger = logging.getLogger(__name__)

class ESNHTTPClient:
    """ESN PULSE HTTP istemcisi.
    
    Bu sınıf:
    1. İnsansı davranış simülasyonu yapar
    2. Rate limit'leri yönetir
    3. Cloudflare korumasını tespit eder
    4. Hataları yönetir
    """
    
    def __init__(self):
        """HTTP istemcisini başlatır."""
        self.session: Optional[ClientSession] = None
        self.user_agents = settings.USER_AGENTS
        self.request_delay = settings.SCRAPING_DELAY
        self.max_retries = settings.MAX_RETRIES
        self.timeout = ClientTimeout(total=settings.REQUEST_TIMEOUT)
    
    async def __aenter__(self) -> "ESNHTTPClient":
        """Context manager entry."""
        print("🔄 Initializing HTTP client...")
        if not self.session:
            print("📡 Creating new aiohttp session...")
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={"User-Agent": random.choice(self.user_agents)}
            )
            print("✅ aiohttp session created")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        print("🔄 Cleaning up HTTP client...")
        if self.session:
            print("🗑️ Closing aiohttp session...")
            await self.session.close()
            self.session = None
            print("✅ aiohttp session closed")
    
    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry_count: int = 0
    ) -> ClientResponse:
        """GET isteği gönderir.
        
        Args:
            url: İstek URL'i
            params: URL parametreleri
            headers: HTTP başlıkları
            retry_count: Yeniden deneme sayısı
        
        Returns:
            HTTP yanıtı
        
        Raises:
            RateLimitError: Rate limit aşıldığında
            CloudflareError: Cloudflare koruması tespit edildiğinde
            NetworkError: Ağ hatası oluştuğunda
            TimeoutError: İstek zaman aşımına uğradığında
        """
        if not self.session:
            print(f"⚠️ Session not initialized for URL: {url}")
            await self.__aenter__()
        
        # İnsansı davranış simülasyonu
        await self._simulate_human_behavior()
        
        try:
            print(f"🌐 Sending GET request to: {url}")
            # İsteği gönder
            response = await self.session.get(
                url,
                params=params,
                headers=headers
            )
            print(f"✅ Response received: {response.status} {response.reason}")
            
            # Yanıtı kontrol et
            await self._check_response(response)
            
            return response
        
        except aiohttp.ClientError as e:
            print(f"❌ Network error for {url}: {str(e)}")
            # Yeniden deneme sayısını kontrol et
            if retry_count < self.max_retries:
                # Üstel geri çekilme
                wait_time = 2 ** retry_count
                print(f"⏳ Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                return await self.get(
                    url,
                    params=params,
                    headers=headers,
                    retry_count=retry_count + 1
                )
            
            raise NetworkError(
                f"HTTP isteği başarısız: {str(e)}",
                url=url
            ) from e
        
        except asyncio.TimeoutError as e:
            print(f"⌛ Timeout error for {url}")
            raise TimeoutError(
                f"HTTP isteği zaman aşımına uğradı: {url}",
                url=url
            ) from e
    
    async def get_with_retry(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        max_retries: Optional[int] = None
    ) -> str:
        """GET isteği gönderir ve yanıt içeriğini döndürür.
        
        Args:
            url: İstek URL'i
            params: URL parametreleri
            headers: HTTP başlıkları
            max_retries: Maksimum yeniden deneme sayısı
        
        Returns:
            Yanıt içeriği
        
        Raises:
            RateLimitError: Rate limit aşıldığında
            CloudflareError: Cloudflare koruması tespit edildiğinde
            NetworkError: Ağ hatası oluştuğunda
            TimeoutError: İstek zaman aşımına uğradığında
        """
        max_retries = max_retries or self.max_retries
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                print(f"🌐 Sending GET request to: {url}")
                print(f"📡 Request parameters: {params}")
                print(f"📨 Request headers: {headers}")
                
                response = await self.get(url, params=params, headers=headers)
                print(f"✅ Response received: {response.status} {response.reason}")
                
                content = await response.text()
                print(f"📄 Response content length: {len(content)} bytes")
                
                if response.status == 200:
                    print(f"✅ Successfully fetched content from: {url}")
                    return content
                elif response.status == 404:
                    print(f"⚠️ Page not found: {url}")
                    return ""  # Boş sayfa döndür, böylece sayfalandırma döngüsü sonlanır
                else:
                    print(f"⚠️ Non-200 status code: {response.status} {response.reason}")
                    return content
                
            except (NetworkError, TimeoutError) as e:
                retry_count += 1
                print(f"❌ Request failed for: {url} (Attempt {retry_count}/{max_retries})")
                print(f"⚠️ Error: {str(e)}")
                
                if retry_count > max_retries:
                    print(f"❌ All retries failed for: {url}")
                    raise
                
                # Üstel geri çekilme
                wait_time = 2 ** retry_count
                print(f"⏳ Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
                
            except (RateLimitError, CloudflareError) as e:
                print(f"⚠️ {str(e)} for: {url}")
                raise
    
    async def head(
        self,
        url: str,
        headers: Optional[Dict] = None,
        retry_count: int = 0
    ) -> ClientResponse:
        """HEAD isteği gönderir.
        
        Args:
            url: İstek URL'i
            headers: HTTP başlıkları
            retry_count: Yeniden deneme sayısı
        
        Returns:
            HTTP yanıtı
        
        Raises:
            RateLimitError: Rate limit aşıldığında
            CloudflareError: Cloudflare koruması tespit edildiğinde
            NetworkError: Ağ hatası oluştuğunda
            TimeoutError: İstek zaman aşımına uğradığında
        """
        if not self.session:
            await self.__aenter__()
        
        # İnsansı davranış simülasyonu
        await self._simulate_human_behavior()
        
        try:
            # İsteği gönder
            response = await self.session.head(
                url,
                headers=headers
            )
            # Yanıtı kontrol et
            await self._check_response(response)
            
            return response
        
        except aiohttp.ClientError as e:
            # Yeniden deneme sayısını kontrol et
            if retry_count < self.max_retries:
                # Üstel geri çekilme
                await asyncio.sleep(2 ** retry_count)
                return await self.head(
                    url,
                    headers=headers,
                    retry_count=retry_count + 1
                )
            
            raise NetworkError(
                f"HTTP isteği başarısız: {str(e)}",
                url=url
            ) from e
        
        except asyncio.TimeoutError as e:
            raise TimeoutError(
                f"HTTP isteği zaman aşımına uğradı: {url}",
                url=url
            ) from e
    
    async def _check_response(self, response: ClientResponse):
        """HTTP yanıtını kontrol eder.
        
        Args:
            response: HTTP yanıtı
        
        Raises:
            RateLimitError: Rate limit aşıldığında
            CloudflareError: Cloudflare koruması tespit edildiğinde
        """
        # HTTP durum kodunu kontrol et
        if response.status == 429:
            raise RateLimitError(
                "Rate limit aşıldı",
                url=str(response.url),
                status_code=response.status
            )
        
        # Cloudflare korumasını kontrol et
        if response.status == 403:
            text = await response.text()
            if "cloudflare" in text.lower():
                raise CloudflareError(
                    "Cloudflare koruması tespit edildi",
                    url=str(response.url),
                    status_code=response.status
                )
    
    async def _simulate_human_behavior(self):
        """İnsansı davranış simülasyonu yapar."""
        # Sabit gecikme
        await asyncio.sleep(self.request_delay)
        
        # Rastgele mola (%5 olasılıkla)
        if random.random() < 0.05:
            await asyncio.sleep(random.uniform(2, 5))
        
        # User-Agent rotasyonu
        if self.session:
            self.session._default_headers["User-Agent"] = random.choice(self.user_agents) 