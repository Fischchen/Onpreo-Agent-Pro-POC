"""Persistence helpers for contacts and call activities."""
from __future__ import annotations

from sqlmodel import Session, select

from app.models import CallActivity, Contact


def _norm(value: str | None) -> str | None:
    """Trim + lowercase for de-dup matching; None-safe."""
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned.lower() if cleaned else None


def upsert_contact(
    session: Session, first_name: str | None, last_name: str | None
) -> Contact | None:
    """Return an existing matching Contact or create one. Returns None if no
    usable name was provided."""
    first_norm = _norm(first_name)
    last_norm = _norm(last_name)
    if first_norm is None and last_norm is None:
        return None

    stmt = select(Contact).where(
        Contact.first_name_norm == (first_norm or ""),
        Contact.last_name_norm == (last_norm or ""),
    )
    existing = session.exec(stmt).first()
    if existing:
        return existing

    contact = Contact(
        first_name=(first_name or "").strip(),
        last_name=(last_name or "").strip(),
        first_name_norm=first_norm or "",
        last_name_norm=last_norm or "",
    )
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


def create_call_activity(
    session: Session,
    title: str | None,
    description: str | None,
    caller_first_name: str | None,
    caller_last_name: str | None,
) -> CallActivity:
    """Persist a call activity, enriching/linking a Contact if a name was given."""
    contact = upsert_contact(session, caller_first_name, caller_last_name)

    activity = CallActivity(
        title=title,
        description=description,
        caller_first_name=caller_first_name,
        caller_last_name=caller_last_name,
        contact_id=contact.id if contact else None,
    )
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity
