import os
import re
import yaml
import logging
from datetime import datetime
from src.models import JobData

logger = logging.getLogger(__name__)

class ObsidianManager:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        # Expand user path
        if self.vault_path.startswith("~"):
            self.vault_path = os.path.expanduser(self.vault_path)
            
        if not os.path.exists(self.vault_path):
            try:
                os.makedirs(self.vault_path)
                logger.info(f"Created Vault Directory: {self.vault_path}")
            except Exception as e:
                logger.error(f"Could not create vault directory: {e}")

    def save_job(self, job: JobData) -> str:
        """Saves job to markdown file. Returns file path."""
        # Sanitize filename
        safe_company = re.sub(r'[\\/*?:"<>|]', "", job.company)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", job.title)
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Limit length
        if len(safe_company) > 20: safe_company = safe_company[:20]
        if len(safe_title) > 30: safe_title = safe_title[:30]
        
        filename = f"{date_str} - {safe_company} - {safe_title}.md"
        file_path = os.path.join(self.vault_path, filename)
        
        # Check duplicate
        if os.path.exists(file_path):
            logger.info(f"File exists, skipping: {filename}")
            return file_path

        # Prepare Frontmatter
        frontmatter = {
            "job_title": job.title,
            "company": job.company,
            "salary": job.salary,
            "location": job.location,
            "link": job.link,
            "tech_stack": job.tech_stack,
            "match_score": job.match_score,
            "status": "待處理",
            "scraped_date": date_str
        }
        
        # Content
        # Use simple string replacement or yaml dump
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=None, sort_keys=False)
        
        content = f"""---
{yaml_str}---

## 🤖 AI 職缺快評
{job.ai_summary or "等待 AI 分析..."}

## 📄 原始職務內容 (JD)
{job.raw_content}
"""
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved to Obsidian: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save obsidian file: {e}")
            return ""
            
        return file_path
