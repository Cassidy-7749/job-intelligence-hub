from pydantic import BaseModel
from typing import List, Optional

class JobData(BaseModel):
    title: str
    company: str
    salary: str
    location: str
    link: str
    source: str  # '104' or 'CakeResume'
    raw_content: str  # Full JD content
    posted_date: Optional[str] = None
    
    # AI Processed fields (optional initially)
    tech_stack: Optional[List[str]] = []
    match_score: Optional[float] = None
    ai_summary: Optional[str] = None
