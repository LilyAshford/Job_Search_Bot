import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///" + os.path.join(os.path.dirname(__file__), "jobs.db?check_same_thread=False")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread" : False})
SessionLocal = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()

# Telegram bot token
TELEGRAM_TOKEN = "your_telegram_token"
TELEGRAM_CHAT_ID = "your_chat_id"

HH_API_URL = "https://api.hh.ru/vacancies"
LINKEDIN_PASSWORD = "your_linkedin_password"
YOUR_EMAIL = "your_email123@gmail.com"

# Default search parameters
DEFAULT_SEARCH_PARAMS = {
"keywords": ["Python"],
"locations": ["Remote"],
"salary_min": 50000,
"experience": "noExperience"
}
