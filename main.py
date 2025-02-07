from playwright.sync_api import sync_playwright, Page
from decouple import config

import requests

from accounts import ACCOUNTS, URL_PARAM


LINKEDIN_EMAIL = config('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = config('LINKEDIN_PASSWORD')

PROXY_SCRAPE_URL = config('PROXY_SCRAPE_URL') 

def fetch_proxies():
    """
    Fetch a list of proxies from ProxyScrape's free proxy list.
    Returns a list of proxies in the format ["ip:port", "ip:port", ...].
    """
    try:
        response = requests.get(PROXY_SCRAPE_URL)
        proxies = response.text.strip().split("\r\n")
        return proxies
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")
        return []

def linkedin_login_with_proxy_rotation():
    proxies = fetch_proxies()
    if not proxies:
        print("No proxies available. Exiting.")
        return

    for proxy_server in proxies:
        print(f"Trying proxy: {proxy_server}")

        with sync_playwright() as p:
            proxy_settings = {
                "server": proxy_server,
            }

            browser = p.chromium.launch(
                headless=False,
            )
            page = browser.new_page()

            try:
                page.goto("https://www.linkedin.com/login", timeout=60000)

                page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
                page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)

                page.click('button[type="submit"]')

                page.wait_for_selector('input[role="combobox"]', state="visible", timeout=60000)

                print("Logged in successfully!")

                for profile_url in ACCOUNTS:
                    print(f"Visiting profile: {profile_url}")
                    page.goto(profile_url, timeout=60000)

                    page.wait_for_selector('h1.KksKnRHKkrgbjGdUsDrVXNzJdONXXPBJY', timeout=60000)
                    full_name = page.query_selector('h1.KksKnRHKkrgbjGdUsDrVXNzJdONXXPBJY').inner_text().strip()

                    """ location_element= page.wait_for_selector('div.not-first-middot > span:first-child', timeout=60000)

                    location = location_element.inner_text().strip() if location_element else "Location not found"
                    print(f"Location: {location}") """

                    print(f"Full Name: {full_name}")
                    print("-" * 40)

                break

            except Exception as e:
                print(f"Proxy {proxy_server} failed: {e}")

            finally:
                browser.close()

if __name__ == "__main__":
    linkedin_login_with_proxy_rotation()

