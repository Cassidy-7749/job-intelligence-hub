import os
import json
import logging
from typing import Optional
from src.models import JobData
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

class JobProcessor:
    def __init__(self, resume_text: str):
        self.resume = resume_text
        self.client = None
        self.model_type = None # 'openai' or 'gemini'
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if genai and gemini_key:
            genai.configure(api_key=gemini_key)
            self.client = genai.GenerativeModel('gemini-pro-latest')
            self.model_type = 'gemini'
            logger.info("Using Gemini AI for processing.")
        elif OpenAI and openai_key:
            self.client = OpenAI(api_key=openai_key)
            self.model_type = 'openai'
            logger.info("Using OpenAI for processing.")
        else:
            logger.warning("No AI API keys found or modules missing. AI features disabled.")

    def process(self, job: JobData) -> JobData:
        if not self.client:
            # Dummy processing if no AI
            job.match_score = 0.0
            job.ai_summary = "AI processing disabled (No Key)."
            return job
            
        try:
            prompt = f"""
            Role: Career Coach & Technical Recruiter.
            Task: Analyze the following Job Description (JD) against the Candidate's Resume.
            
            Candidate Resume:
            {self.resume}
            
            Job Description:
            {job.raw_content}
            {job.title} at {job.company}
            
            Output JSON format only:
            {{
                "tech_stack": ["list", "of", "technologies"],
                "match_score": 0.0 to 10.0,
                "summary": "Brief summary in Traditional Chinese (max 100 words), highlighting key requirements.",
                "pros": ["pro1", "pro2"],
                "cons": ["con1", "con2"]
            }}
            """
            
            if self.model_type == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={ "type": "json_object" }
                )
                content = response.choices[0].message.content
            else: # gemini
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                content = response.text
            data = json.loads(content)
            
            job.tech_stack = data.get("tech_stack", [])
            job.match_score = float(data.get("match_score", 0))
            job.ai_summary = data.get("summary", "No summary")
            
            # Additional metadata could be stored if JobData supported it
            # For now we stick to schema
            
        except Exception as e:
            logger.error(f"AI Processing failed for {job.title}: {e}")
            job.ai_summary = f"AI Error: {e}"
            
        return job
