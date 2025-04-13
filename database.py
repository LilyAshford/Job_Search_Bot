from sqlalchemy.orm import Session
from models import UserSettings

def get_user_settings(db: Session, user_id: int):
    return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

def update_user_settings(db: Session, user_id: int, settings: dict):
    db_settings = get_user_settings(db, user_id)
    if db_settings:
        db_settings.keywords = settings.get("keywords", db_settings.keywords)
        db_settings.locations = settings.get("locations", db_settings.locations)
        db_settings.salary_min = settings.get("salary_min", db_settings.salary_min)
        db_settings.experience = settings.get("experience", db_settings.experience)
    else:
        db_settings = UserSettings(
            user_id=user_id,
            keywords=settings["keywords"],
            locations=settings["locations"],
            salary_min=settings["salary_min"],
            experience=settings["experience"]
        )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

