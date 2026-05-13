import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level up from this package)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-2.0-flash"

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = "llama-3.3-70b-versatile"

MAX_COMPANIES: int = 20          # max unique companies to score
MAX_RESULTS_PER_QUERY: int = 5   # DuckDuckGo results per query
SCRAPE_TIMEOUT: int = 10         # seconds per site
SCRAPE_DELAY: float = 0.5        # polite delay between scrapes (seconds)
RAW_TEXT_LIMIT: int = 2500       # chars of visible text passed to scorer
