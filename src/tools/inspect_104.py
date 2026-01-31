import asyncio
from playwright.async_api import async_playwright

async def handle_response(response):
    if "jobs/search" in response.url and "json" in response.headers.get("content-type", ""):
        print(f"FOUND API: {response.url}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("response", handle_response)
        
        url = "https://www.104.com.tw/jobs/search/?keyword=Java&jobsource=index_s&ro=0&mode=s&order=11"
        try:
            print(f"Navigating to {url}")
            await page.goto(url)
            await asyncio.sleep(8)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
