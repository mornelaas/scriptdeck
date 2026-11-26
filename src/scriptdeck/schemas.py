from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from scriptdeck.models import ScriptStatus


class ScriptBase(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    platform: str | None = None
    hook: str | None = None
    notes: str | None = None
    creator_id: int | None = None


class ScriptCreate(ScriptBase):
    pass


class ScriptUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=120)
    status: ScriptStatus | None = None
    platform: str | None = None
    hook: str | None = None
    notes: str | None = None
    creator_id: int | None = None


class ScriptOut(ScriptBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: ScriptStatus
    created_at: datetime
    updated_at: datetime


class CreatorBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    niche: str | None = None
    handle: str | None = None


class CreatorCreate(CreatorBase):
    pass


class CreatorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    niche: str | None = None
    handle: str | None = None


class CreatorOut(CreatorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=15, max_length=128)


class UserOut(BaseModel):
    """Show the user, but never show the password or hash."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    created_at: datetime
