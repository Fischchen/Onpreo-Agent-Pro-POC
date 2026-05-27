"""Streamlit viewer for stored contacts and call activities.

Run:  uv run streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlmodel import select

from app.db import get_session
from app.models import CallActivity, Contact

st.set_page_config(page_title="Onpreo Call Activities POC", layout="wide")
st.title("Onpreo Call Activities POC")

if st.button("🔄 Refresh"):
    st.rerun()

with get_session() as session:
    contacts = session.exec(select(Contact).order_by(Contact.created_at.desc())).all()
    activities = session.exec(
        select(CallActivity).order_by(CallActivity.created_at.desc())
    ).all()
    contact_name = {c.id: f"{c.first_name} {c.last_name}".strip() for c in contacts}

st.header(f"Call Activities ({len(activities)})")
if activities:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "id": a.id,
                    "created_at": a.created_at,
                    "title": a.title,
                    "description": a.description,
                    "caller": f"{a.caller_first_name or ''} {a.caller_last_name or ''}".strip(),
                    "linked_contact": contact_name.get(a.contact_id),
                }
                for a in activities
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No call activities yet. Call the MCP tool to create one.")

st.header(f"Contacts ({len(contacts)})")
if contacts:
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "id": c.id,
                    "created_at": c.created_at,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                }
                for c in contacts
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No contacts yet.")
