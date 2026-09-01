from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import Skill


def seed_database(db: Session) -> None:
    if db.query(Skill).first():
        return

    today = date.today()
    sample_skills = [
        Skill(
            name="Python",
            category="Backend",
            current_level=3,
            target_level=8,
            progress_percentage=38,
            last_practiced_date=today - timedelta(days=4),
        ),
        Skill(
            name="FastAPI",
            category="Web Development",
            current_level=2,
            target_level=6,
            progress_percentage=33,
            last_practiced_date=today - timedelta(days=12),
        ),
        Skill(
            name="SQLAlchemy",
            category="Database",
            current_level=4,
            target_level=7,
            progress_percentage=57,
            last_practiced_date=today - timedelta(days=5),
        ),
    ]

    db.add_all(sample_skills)
    db.commit()
