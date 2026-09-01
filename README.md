# SkillTrack – Personal Skill Progress Tracker

SkillTrack is a simple FastAPI project designed for students and early-career developers to track learning progress across technical skills. It helps a person decide what to practice next based on progress, target level, and how long it has been since the last practice session.

Why it was built:
- To make personal learning progress visible and easy to manage.
- To help students show a practical, real-world project on a resume.
- To keep the project beginner-friendly enough to explain clearly in interviews.

## Features
- Add new skills with category and target goals.
- View all saved skills in one place.
- Update current level, target level, and practice date.
- Delete skills you no longer want to track.
- Get a recommendation for the next skill to practice.
- Swagger documentation is available automatically through FastAPI.

## Tech stack
- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Pytest

## Project structure

skilltrack-personal-progress-tracker/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
├── tests/
│   └── test_skill_api.py
├── .gitignore
├── README.md
├── requirements.txt
├── skilltrack.db
└── .venv/

## Installation

From the project root, create a virtual environment and install dependencies:

```bash
py -3.13 -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the application

```bash
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/docs for Swagger UI
- http://127.0.0.1:8000/redoc for ReDoc

## Run tests

```bash
pytest
```

## Sample data

The app automatically inserts a few starter skills when the database is empty, so the project is easy to explore without manually creating records.

Example skills included:
- Python
- FastAPI
- SQLAlchemy
- Data Structures

## Example API requests

### Add a skill

```bash
curl -X POST "http://127.0.0.1:8000/skills" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python",
    "category": "Backend",
    "current_level": 3,
    "target_level": 8,
    "last_practiced_date": "2026-09-01"
  }'
```

### View all skills

```bash
curl http://127.0.0.1:8000/skills
```

### Update skill progress

```bash
curl -X PATCH "http://127.0.0.1:8000/skills/1/progress" \
  -H "Content-Type: application/json" \
  -d '{
    "current_level": 5,
    "target_level": 8,
    "last_practiced_date": "2026-09-02"
  }'
```

### Get next practice recommendation

```bash
curl http://127.0.0.1:8000/skills/recommendation
```

### Delete a skill

```bash
curl -X DELETE "http://127.0.0.1:8000/skills/1"
```

## Example responses

### Create skill response

```json
{
  "id": 1,
  "name": "Python",
  "category": "Backend",
  "current_level": 3,
  "target_level": 8,
  "last_practiced_date": "2026-09-01",
  "progress_percentage": 38,
  "created_at": "2026-09-02T00:08:12",
  "updated_at": "2026-09-02T00:08:12"
}
```

### Next practice recommendation response

```json
{
  "skill_id": 2,
  "name": "FastAPI",
  "category": "Web Development",
  "current_level": 2,
  "target_level": 6,
  "progress_percentage": 33,
  "reason": "This skill has the lowest progress (33%) and has not been practiced in 12 day(s)."
}
```

## Why this project is useful

This project is intentionally simple, but it mirrors the kind of work a fresh graduate might build in a real learning phase:
- a backend service with a database,
- CRUD APIs,
- validation and error handling,
- a practical recommendation feature,
- and a test suite.

It is easy to explain during an interview because every file and endpoint has a clear job.

## Notes

The project intentionally avoids complicated architecture, cloud tools, or advanced system design. It focuses on a clean, readable implementation that can be understood and explained by a beginner or junior developer.
