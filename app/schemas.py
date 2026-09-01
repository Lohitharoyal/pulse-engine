from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SkillBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    category: str = Field(..., min_length=2, max_length=50)
    current_level: int = Field(..., ge=1, le=10)
    target_level: int = Field(..., ge=1, le=10)
    last_practiced_date: date | None = None

    @field_validator("name", "category")
    @classmethod
    def strip_spaces(cls, value: str) -> str:
        if not value:
            return value
        return value.strip()

    @model_validator(mode="after")
    def validate_levels(self):
        if self.current_level > self.target_level:
            raise ValueError("current_level cannot be greater than target_level.")
        return self


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    current_level: int | None = Field(default=None, ge=1, le=10)
    target_level: int | None = Field(default=None, ge=1, le=10)
    last_practiced_date: date | None = None

    @field_validator("name", "category")
    @classmethod
    def strip_spaces(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @model_validator(mode="after")
    def validate_levels(self):
        current = self.current_level
        target = self.target_level

        if current is not None and target is not None and current > target:
            raise ValueError("current_level cannot be greater than target_level.")

        return self


class SkillProgressUpdate(BaseModel):
    current_level: int | None = Field(default=None, ge=1, le=10)
    target_level: int | None = Field(default=None, ge=1, le=10)
    last_practiced_date: date | None = None

    @model_validator(mode="after")
    def validate_levels(self):
        current = self.current_level
        target = self.target_level

        if current is not None and target is not None and current > target:
            raise ValueError("current_level cannot be greater than target_level.")

        return self


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    progress_percentage: int
    created_at: datetime
    updated_at: datetime


class NextPracticeResponse(BaseModel):
    skill_id: int
    name: str
    category: str
    current_level: int
    target_level: int
    progress_percentage: int
    reason: str