"""SQLModel tables: Contact (CRM record) and CallActivity (logged call)."""
from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.utcnow()


class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    # Normalized (trim + lowercase) keys used for de-duplication on upsert.
    first_name_norm: str = Field(index=True)
    last_name_norm: str = Field(index=True)
    created_at: datetime = Field(default_factory=_utcnow)


class CallActivity(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str | None = None
    description: str | None = None
    # Raw capture of whatever the caller stated on the call.
    caller_first_name: str | None = None
    caller_last_name: str | None = None
    # Linked Contact when a name was provided; null otherwise.
    contact_id: int | None = Field(default=None, foreign_key="contact.id")
    created_at: datetime = Field(default_factory=_utcnow)
