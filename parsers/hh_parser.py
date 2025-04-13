import requests
import logging
from typing import List, Dict
from database import get_user_settings
from config import SessionLocal

logger = logging.getLogger(__name__)

def parse_hh(user_id: int) -> List[Dict]:
    db = SessionLocal()
    try:
        settings = get_user_settings(db, user_id)
        if not settings:
            return []

        params = {
        "text": " AND ".join(settings.keywords),
        "search_field": "name",
        "area": get_area_ids(settings.locations),
        "salary": settings.salary_min,
        "experience": settings.experience,
        "per_page": 20,
        "page": 0
        }

        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()

        return [format_vacancy(item) for item in response.json().get('items', [])]

    except Exception as e:
        logger.error(f"HH parsing error: {e}")
        return []
    finally:
        db.close()

def get_area_ids(locations: List[str]) -> List[int]:
    area_map = {
    "Moscow": 1,
    "Saint Petersburg": 2,
    "Remote": 113,
    "New York": 124,
    }
    return [area_map.get(loc, 113) for loc in locations]

def format_vacancy(item: Dict) -> Dict:
    return {
    "title": item.get('name'),
    "company": item.get('employer', {}).get('name'),
    "salary": format_salary(item.get('salary')),
    "url": item.get('alternate_url'),
    "source": "HeadHunter"
    }

def format_salary(salary: Dict) -> str:
    if not salary:
        return "Not specified"
    return f"{salary.get('from')}-{salary.get('to')} {salary.get('currency')}"