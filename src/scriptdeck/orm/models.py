from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..models import ScriptStatus


class Base(DeclarativeBase):
    """Registry for every ORM model of ScriptDeck."""


class Creator(Base):
    """A content creator. Maps the existing creators table."""

    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    niche: Mapped[str | None]
    handle: Mapped[str | None]
    created_at: Mapped[str]

    scripts: Mapped[list["Script"]] = relationship(back_populates="creator")


class Script(Base):
    """A script in its lifecycle. Maps the existing scripts table."""

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    status: Mapped[ScriptStatus] = mapped_column(
        SAEnum(
            ScriptStatus,
            values_callable=lambda enum: [member.value for member in enum],
        )
    )
    platform: Mapped[str | None]
    hook: Mapped[str | None]
    notes: Mapped[str | None]
    created_at: Mapped[str]
    updated_at: Mapped[str]
    creator_id: Mapped[int | None] = mapped_column(ForeignKey("creators.id"))

    creator: Mapped["Creator | None"] = relationship(back_populates="scripts")
