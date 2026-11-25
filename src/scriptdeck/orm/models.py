from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, MetaData, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from ..models import ScriptStatus


class Base(DeclarativeBase):
    """Registry for every ORM model of ScriptDeck."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class Creator(Base):
    """A content creator. Maps the existing creators table."""

    __tablename__ = "creators"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    niche: Mapped[str | None]
    handle: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )

    scripts: Mapped[list["Script"]] = relationship(
        back_populates="creator", cascade="all, delete", passive_deletes=True
    )


class Script(Base):
    """A script in its lifecycle. Maps the existing scripts table."""

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    status: Mapped[ScriptStatus] = mapped_column(
        SAEnum(
            ScriptStatus,
            values_callable=lambda enum: [member.value for member in enum],
        ),
        server_default="idea",
        index=True,
    )
    platform: Mapped[str | None]
    hook: Mapped[str | None]
    notes: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("creators.id", ondelete="CASCADE"), index=True
    )

    creator: Mapped["Creator | None"] = relationship(back_populates="scripts")
