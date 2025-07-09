from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    GROQ_MODEL = os.getenv("GROQ_MODEL")

settings = Settings()
