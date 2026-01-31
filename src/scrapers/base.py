from abc import ABC, abstractmethod
from typing import List
from src.models import JobData

class BaseScraper(ABC):
    @abstractmethod
    async def scrape(self, keywords: List[str], locations: List[str] = None, max_jobs: int = 10) -> List[JobData]:
        """
        Scrape jobs from the source.
        
        Args:
            keywords: List of keywords to search for.
            max_jobs: Maximum number of jobs to fetch.
            
        Returns:
            List of JobData objects.
        """
        pass
