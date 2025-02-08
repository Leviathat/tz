import aiohttp
import asyncio
from typing import List, AsyncGenerator
import logging
import requests
from datetime import datetime
from decouple import config

PROXY_SCRAPE_URL = config('PROXY_SCRAPE_URL') 

class ProxyManager:
    def __init__(self, test_url: str = "https://www.linkedin.com", timeout: float = 2.0):
        self.test_url = test_url
        self.timeout = timeout
        self.working_proxies: List[str] = []
        self.current_index = 0
        self.logger = logging.getLogger(__name__)
        self.last_test_time = None

    def fetch_proxies(self) -> List[str]:
        """Fetch proxies from ProxyScrape."""
        try:
            response = requests.get(
                PROXY_SCRAPE_URL
            )
            proxies = response.text.strip().split("\r\n")
            self.logger.info(f"Fetched {len(proxies)} proxies")
            return proxies
        except Exception as e:
            self.logger.error(f"Failed to fetch proxies: {e}")
            return []

    async def test_proxy(self, proxy: str) -> bool:
        """Test if proxy works with LinkedIn within timeout."""
        try:
            start_time = datetime.now()
            async with aiohttp.ClientSession() as session:
                proxy_url = f"http://{proxy}"
                async with session.get(
                    self.test_url,
                    proxy=proxy_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        elapsed = (datetime.now() - start_time).total_seconds()
                        return elapsed <= self.timeout
                    return False
        except Exception as e:
            self.logger.debug(f"Proxy {proxy} failed: {e}")
            return False

    async def initialize(self) -> None:
        """Initialize by fetching and testing proxies."""
        self.logger.info("Initializing proxy manager...")
        proxies = self.fetch_proxies()
        
        if not proxies:
            raise RuntimeError("No proxies available")

        # Test proxies concurrently
        tasks = [self.test_proxy(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)
        
        # Store working proxies
        self.working_proxies = [
            proxy for proxy, works in zip(proxies, results) if works
        ]
        
        self.last_test_time = datetime.now()
        
        if not self.working_proxies:
            raise RuntimeError("No working proxies found")
        
        self.logger.info(f"Found {len(self.working_proxies)} working proxies")

    async def get_proxies(self) -> AsyncGenerator[str, None]:
        """
        Async generator that yields working proxies.
        Automatically rotates through the proxy list.
        """
        if not self.working_proxies:
            await self.initialize()
        
        while True:
            for proxy in self.working_proxies:
                yield proxy
            
            # After going through all proxies, retest them
            self.logger.info("Retesting proxies...")
            await self.initialize()
            
            if not self.working_proxies:
                self.logger.error("No more proxies available after retest")
                break

proxy_manager = ProxyManager(timeout=2.0)

# Example usage
async def main():
    
    try:
        async for proxy in proxy_manager.get_proxies():
            print(f"Using proxy: {proxy}")
            # Your scraping logic here
            # Break after first successful proxy for this example
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
