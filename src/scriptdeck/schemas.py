from datetime import datetime

from pydantic import BaseModel, Field

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
    id: int
    created_at: datetime
