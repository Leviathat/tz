from playwright.sync_api import sync_playwright
import asyncio
from playwright.async_api import async_playwright

async def scrape_text(url: str, proxy: str) -> str:
    proxy_settings = {
        "server": proxy,
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy=proxy_settings
        ) 
        
        try:
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(url)
            
            full_name_selector = 'h1.top-card-layout__title'
            await page.wait_for_selector(full_name_selector, timeout=60000)

            full_name_element = await page.query_selector(full_name_selector)
            full_name_text = await full_name_element.inner_text()
            
            location_selector = 'div.not-first-middot'
            await page.wait_for_selector(location_selector, timeout=60000)

            location_element = await page.query_selector(location_selector)
            location_text = await location_element.inner_text()


            
            return (full_name_text, location_text)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            raise
            
        finally:
            await browser.close()

async def main():
    url = "https://www.linkedin.com/in/reidhoffman"
    
    try:
        name, location = await scrape_text(url)
        print(f"Scraped text: {name}")
        print(f"Scraped text: {location}")
    except Exception as e:
        print(f"Failed to scrape: {e}")

if __name__ == "__main__":
    asyncio.run(main())
