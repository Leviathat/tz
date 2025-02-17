# main.py
import asyncio
import pandas as pd
from proxies import ProxyManager, proxy_manager
from linkedin import scraper
import logging
from typing import Tuple

class ExcelProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.logger = logging.getLogger(__name__)

    def _split_name(self, full_name: str) -> Tuple[str, str]:
        """Split full name into first and last name."""
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], ""
        return parts[0], " ".join(parts[1:])

    async def process_profiles(self):
        """Process all LinkedIn profiles in the Excel file."""
        proxy_manager = ProxyManager(timeout=2.0)

        for index, row in self.df.iterrows():
            url = row['prooflink']
            if pd.isna(url) or not isinstance(url, str):
                continue

            try:
                self.logger.info(f"Processing profile: {url}")
                
                async for proxy in proxy_manager.get_proxies():
                    result = await scraper.scrape(url, proxy)
                    
                    if result:
                        name, location = result
                        first_name, last_name = self._split_name(name)

                        self.df.at[index, 'first_name'] = first_name
                        self.df.at[index, 'last_name'] = last_name
                        self.df.at[index, 'geo'] = location
                        
                        self.save_excel()
                        
                        self.logger.info(f"Successfully processed {name}")
                        break
                    else:
                        self.logger.error(f"Failed to scrape profile: {url}")

            except Exception as e:
                self.logger.error(f"Error processing {url}: {e}")
                continue

    def save_excel(self):
        """Save the updated DataFrame to Excel."""
        try:
            self.df.to_excel(self.file_path, index=False)
            self.logger.info("Excel file updated successfully")
        except Exception as e:
            self.logger.error(f"Error saving Excel file: {e}")

async def test():
    url = "https://www.linkedin.com/in/reidhoffman"

    async for proxy in proxy_manager.get_proxies():
        print(f"Testing proxy: {proxy}")
        name, location = None, None

        while not name or not location:
            try:
                name, location = await scraper.scrape(url, proxy)
            except Exception as e:
                print(f"Failed to scrape: {e}")

        return name, location
    
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        processor = ExcelProcessor('linkedin_profiles.xlsx')
        
        await processor.process_profiles()
        
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")

if __name__ == "__main__":
    asyncio.run(main())
