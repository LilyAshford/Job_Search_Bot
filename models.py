from sqlalchemy import Column, Integer, String, JSON
from config import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, primary_key=True)
    keywords = Column(JSON, nullable=False)
    locations = Column(JSON, nullable=False)
    salary_min = Column(Integer, nullable=False)
    experience = Column(String, nullable=False)

    def to_dict(self):
        return {
        "keywords": self.keywords,
        "locations": self.locations,
        "salary_min": self.salary_min,
        "experience": self.experience
        }
