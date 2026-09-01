from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.models import Skill
from app.schemas import (
    NextPracticeResponse,
    SkillCreate,
    SkillProgressUpdate,
    SkillResponse,
    SkillUpdate,
)
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="SkillTrack - Personal Skill Progress Tracker",
    description="A simple learning tracker for managing skill goals and planning the next practice session.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SkillTrack! Use /docs for the API documentation.",
        "project": "SkillTrack",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "skilltrack"}


def calculate_progress_percentage(current_level: int, target_level: int) -> int:
    if target_level <= 0:
        return 0
    percent = round((current_level / target_level) * 100)
    return max(0, min(100, percent))


@app.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    existing_skill = db.query(Skill).filter(Skill.name.ilike(skill.name)).first()
    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A skill with this name already exists.",
        )

    db_skill = Skill(
        name=skill.name.strip(),
        category=skill.category.strip(),
        current_level=skill.current_level,
        target_level=skill.target_level,
        last_practiced_date=skill.last_practiced_date,
        progress_percentage=calculate_progress_percentage(skill.current_level, skill.target_level),
    )

    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill


@app.get("/skills", response_model=list[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    return db.query(Skill).order_by(Skill.progress_percentage.asc(), Skill.last_practiced_date.asc()).all()


@app.get("/skills/recommendation", response_model=NextPracticeResponse)
def next_practice_recommendation(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    if not skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No skills exist yet. Add a skill before requesting a recommendation.",
        )

    def stale_days(skill: Skill) -> int:
        if not skill.last_practiced_date:
            return 999
        return (date.today() - skill.last_practiced_date).days

    recommended = min(
        skills,
        key=lambda skill: (skill.progress_percentage, stale_days(skill), skill.name.lower()),
    )

    reason = (
        f"This skill has the lowest progress ({recommended.progress_percentage}%) and has not been practiced "
        f"in {stale_days(recommended)} day(s)."
        if recommended.last_practiced_date
        else f"This skill has the lowest progress ({recommended.progress_percentage}%) and has not been practiced recently."
    )

    return NextPracticeResponse(
        skill_id=recommended.id,
        name=recommended.name,
        category=recommended.category,
        current_level=recommended.current_level,
        target_level=recommended.target_level,
        progress_percentage=recommended.progress_percentage,
        reason=reason,
    )


@app.get("/skills/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} was not found.",
        )
    return skill


@app.put("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, skill_update: SkillUpdate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} was not found.",
        )

    if skill_update.name is not None:
        duplicate = db.query(Skill).filter(Skill.name.ilike(skill_update.name), Skill.id != skill_id).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another skill with this name already exists.",
            )
        skill.name = skill_update.name.strip()

    if skill_update.category is not None:
        skill.category = skill_update.category.strip()

    if skill_update.current_level is not None:
        skill.current_level = skill_update.current_level

    if skill_update.target_level is not None:
        skill.target_level = skill_update.target_level

    if skill_update.last_practiced_date is not None:
        skill.last_practiced_date = skill_update.last_practiced_date

    skill.progress_percentage = calculate_progress_percentage(skill.current_level, skill.target_level)

    db.commit()
    db.refresh(skill)
    return skill


@app.patch("/skills/{skill_id}/progress", response_model=SkillResponse)
def update_skill_progress(skill_id: int, progress_update: SkillProgressUpdate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} was not found.",
        )

    if progress_update.current_level is not None:
        skill.current_level = progress_update.current_level

    if progress_update.target_level is not None:
        skill.target_level = progress_update.target_level

    if progress_update.last_practiced_date is not None:
        skill.last_practiced_date = progress_update.last_practiced_date

    skill.progress_percentage = calculate_progress_percentage(skill.current_level, skill.target_level)

    db.commit()
    db.refresh(skill)
    return skill


@app.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_id} was not found.",
        )

    db.delete(skill)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
