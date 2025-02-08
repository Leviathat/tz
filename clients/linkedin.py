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
        self.headless = False


    async def login(self, page: Page):
        await page.goto("https://www.linkedin.com/login", timeout=60000)

        await page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        await page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)

        await page.click('button[type="submit"]')

        await page.wait_for_selector('img.feed-identity-module__member-bg-image', state="visible", timeout=60000)

        return page
    

    async def get_profile_info(self, page: Page, url: str):
        try:
            await page.goto(url)
            
            dismiss_button_selector = 'button.modal__dismiss'
            if await page.query_selector(dismiss_button_selector):
                await page.click(dismiss_button_selector)
                
            full_name_selector = '#ember36'
            location_selector = 'div.mt2 > span.text-body-small'

            if not self.auth_required:
                full_name_selector = "top-card-layout__title"
                location_selector = 'div.not-first-middot > span:first-child'

            await page.wait_for_selector(full_name_selector, timeout=60000) 
            element = await page.query_selector(full_name_selector)
            full_name_text = await element.inner_text()

            await page.wait_for_selector(location_selector, timeout=60000)
            location_element = await page.query_selector(location_selector)
            location_text = await location_element.inner_text()
            
            return full_name_text, location_text.strip()
        except Exception as e:
            print(f"Error during scraping: {e}")


    async def scrape_profile(self, url: str, proxy: str = None):
        if not proxy:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless
                )

                context = await browser.new_context()
                page = await context.new_page()

                if self.auth_required:
                    page = await self.login(page)

                name, location = await self.get_profile_info(page, url)

                self.logger.info(f"Scraped name: {name}")
                self.logger.info(f"Scraped location: {location}")

                return name, location
            
        proxy_settings = {
            "server": proxy,
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                proxy=proxy_settings
            )

            context = await browser.new_context()
            page = await context.new_page()

            if self.auth_required:
                page = await self.login(page)

            name, location = await self.get_profile_info(page, url)

            self.logger.info(f"Scraped name: {name}")
            self.logger.info(f"Scraped location: {location}")

            return name, location
        

    async def scrape(self, url: str, proxy: str = None):
        try:
            name, location = await self.scrape_profile(url, proxy)
            print(f"Scraped name: {name}")
            print(f"Scraped location: {location}")
        except Exception as e:
            print(f"Failed to scrape: {e}")
            
scraper = LinkedInScraper()


async def main():
    url = "https://www.linkedin.com/in/reidhoffman"
    
    await scraper.scrape(url)


if __name__ == "__main__":
    asyncio.run(main())
