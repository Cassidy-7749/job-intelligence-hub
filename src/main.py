import asyncio
import os
import logging
from dotenv import load_dotenv
import sys

# Ensure src is in path
# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.one_zero_four import OneZeroFourScraper
from src.ai.processor import JobProcessor
from src.obsidian.manager import ObsidianManager

# Load env from root
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("Main")

async def run():
    print("=== Job Intelligence Hub Started ===")
    
    # Configuration
    keywords_env = os.getenv("SEARCH_KEYWORDS", "Java")
    keywords = [k.strip() for k in keywords_env.split(",")]
    
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./obsidian_output")
    resume_path = os.getenv("RESUME_PATH", "resume.txt")
    
    logger.info(f"Keywords: {keywords}")
    logger.info(f"Vault: {vault_path}")
    
    # Initialize Folder
    if not os.path.exists(vault_path):
        os.makedirs(vault_path)
        
    # Read Resume
    resume_content = "Experienced Java Developer with Spring Boot skills."
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_content = f.read()
    else:
        logger.warning(f"Resume not found at {resume_path}, using default placeholder.")

    # Initialize Components
    scraper = OneZeroFourScraper()
    ai_processor = JobProcessor(resume_content)
    obsidian_manager = ObsidianManager(vault_path)
    
    # 1. Scrape
    logger.info(">>> Step 1: Scraping Jobs...")
    jobs = await scraper.scrape(keywords=keywords, max_jobs=5)
    logger.info(f"Scraped {len(jobs)} jobs.")
    
    if not jobs:
        logger.warning("No jobs found. Accessing mock data fallback was likely triggered inside scraper.")
    
    # 2. Process & Save
    logger.info(">>> Step 2: AI Processing and Saving to Obsidian...")
    saved_count = 0
    for job in jobs:
        logger.info(f"Processing: {job.title} @ {job.company}")
        
        # AI Enrich
        processed_job = ai_processor.process(job)
        
        # Save
        path = obsidian_manager.save_job(processed_job)
        if path:
            saved_count += 1
            
    logger.info(f"=== Done. Saved {saved_count} jobs to {vault_path} ===")

if __name__ == "__main__":
    asyncio.run(run())
