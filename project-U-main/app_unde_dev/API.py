import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("API_KEY")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com/v1")
    API_SEARCH_ENDPOINT = os.getenv("API_SEARCH_ENDPOINT", "/search")

