import asyncio
import logging
import random
from typing import List, Optional
from playwright.async_api import async_playwright
from src.scrapers.base import BaseScraper
from src.models import JobData

logger = logging.getLogger(__name__)

class OneZeroFourScraper(BaseScraper):
    async def scrape(self, keywords: List[str], max_jobs: int = 10) -> List[JobData]:
        all_jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = await context.new_page()
            
            for keyword in keywords:
                if len(all_jobs) >= max_jobs:
                    break
                    
                print(f"Starting scrape for keyword: {keyword}")
                captured_limit = max_jobs - len(all_jobs)
                api_jobs_data = [] # Local to keyword
                
                url = f"https://www.104.com.tw/jobs/search/?keyword={keyword}&jobsource=index_s&ro=0&mode=s&order=11"
                
                try:
                    # Robust wait for API response
                    async with page.expect_response(
                        lambda response: "jobs/search/api" in response.url, 
                        timeout=15000
                    ) as response_info:
                        await page.goto(url, wait_until="domcontentloaded")
                    
                    response = await response_info.value
                    print(f"Captured API Response: {response.url}")
                    
                    try:
                        data = await response.json()
                        if "data" in data and "list" in data["data"]:
                            items = data["data"]["list"]
                            api_jobs_data.extend(items)
                            print(f"Extracted {len(items)} items from API")
                    except Exception as e:
                        print(f"Failed to parse JSON: {e}")
                        
                except Exception as e:
                    logger.error(f"Error scraping {keyword}: {e}")
                    # Continue to next keyword or try to list items from DOM
                    # DOM Fallback?
                
                # Process Data
                for j in api_jobs_data:
                    if len(all_jobs) >= max_jobs: break
                    
                    title = j.get('jobName', 'Unknown')
                    company = j.get('custName', 'Unknown')
                    link_info = j.get('link', {})
                    link = link_info.get('jobUrl')
                    if link and link.startswith("//"): link = "https:" + link
                    
                    if not link or any(job.link == link for job in all_jobs): continue

                    print(f"Fetching details: {title}")
                    raw_content = j.get('description', '') 
                    
                    # Fetch Detail
                    try:
                        detail_page = await context.new_page()
                        await detail_page.goto(link, wait_until="domcontentloaded")
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        if await detail_page.locator("p.job-description__content").count() > 0:
                            raw_content = await detail_page.locator("p.job-description__content").first.text_content()
                        elif await detail_page.locator("div.job-description-table").count() > 0:
                            raw_content = await detail_page.locator("div.job-description-table").first.text_content()
                        
                        await detail_page.close()
                    except Exception as e:
                        logger.warning(f"Detail fetch failed: {e}")
                        if 'detail_page' in locals(): await detail_page.close()
                    
                    job = JobData(
                        title=title,
                        company=company,
                        salary=f"{j.get('salaryLow',0)} - {j.get('salaryHigh',0)}",
                        location=j.get('jobAddrNoDesc', 'Unknown'),
                        link=link,
                        source="104",
                        raw_content=raw_content.strip(),
                        posted_date=j.get('appearDate', '')
                    )
                    all_jobs.append(job)
            
            await browser.close()
            
        # Mock Data Fallback
        if not all_jobs:
            print("WARNING: No jobs found. Loading Mock Data for development.")
            try:
                import json
                import os
                mock_path = 'src/data/sample_jobs.json'
                if os.path.exists(mock_path):
                    with open(mock_path, 'r', encoding='utf-8') as f:
                        mock_data = json.load(f)
                    for j in mock_data:
                        link_info = j.get('link', {})
                        link = link_info.get('jobUrl')
                        if link and link.startswith('//'): link = 'https:' + link
                        
                        all_jobs.append(JobData(
                            title=j.get('jobName'),
                            company=j.get('custName'),
                            salary=f"{j.get('salaryLow')} - {j.get('salaryHigh')}",
                            location=j.get('jobAddrNoDesc'),
                            link=link or "https://www.104.com.tw",
                            source="104",
                            raw_content=j.get('description', ''),
                            posted_date=j.get('appearDate', '')
                        ))
            except Exception as e:
                print(f"Failed to load mock data: {e}")
                
        return all_jobs
