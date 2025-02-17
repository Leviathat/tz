from playwright.async_api import async_playwright, Page
from typing import Tuple, Optional
import logging
import asyncio

from decouple import config

LINKEDIN_EMAIL = config('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = config('LINKEDIN_PASSWORD')

class LinkedInScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auth_required = False
        self.headless = True

        self.full_name_selector = "h1.top-card-layout__title"
        self.location_selector = "div.not-first-middot > span:first-child"

    async def get_profile_info(self, page: Page, url: str):
        try:
            await page.goto(url)
        

            await page.wait_for_selector(self.full_name_selector, timeout=2000) 
            element = await page.query_selector(self.full_name_selector)
            full_name_text = await element.inner_text()
 
            await page.wait_for_selector(self.location_selector, timeout=60000)
            location_element = await page.query_selector(self.location_selector)
            location_text = await location_element.inner_text()
            
            return full_name_text, location_text

        except Exception as e:
            print(f"Error during scraping: {e}")
  

    async def scrape(self, url: str, proxy: str = None):
        async with async_playwright() as p:
            if proxy:
                proxy_settings = {
                    "server": proxy,
                }
                browser = await p.chromium.launch(
                    headless=self.headless,
                    proxy=proxy_settings
                )
            else:
                browser = await p.chromium.launch(
                    headless=self.headless
                )

            context = await browser.new_context()
            page = await context.new_page()

            name, location = await self.get_profile_info(page, url)

            print(f"Scraped name: {name}")
            print(f"Scraped location: {location}")

            return name, location
            
scraper = LinkedInScraper()

async def main():
    url = "https://www.linkedin.com/in/reidhoffman"

    await scraper.scrape(url)


if __name__ == "__main__":
    asyncio.run(main())
