from pathlib import Path
import streamlit as st

CSS_PATH = Path(__file__).parent / "assets" / "style.css"


def load_css():
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def kpi_card(icon, value, label, note, color="red", note_type="up"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon kpi-{color}">{icon}</div>
            <div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-note {note_type}">{note}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    

def topbar(user_name, role, unread):
    words = [w for w in user_name.replace("Dr. ", "").split() if w]
    initials = "".join(w[0] for w in words[:2]).upper()

    search_col, bell_col, user_col = st.columns([5, 0.8, 2.4], vertical_alignment="center")

    with search_col:
        st.text_input(
            "Search",
            placeholder="🔍 Search donors, units, requests...",
            label_visibility="collapsed",
            key="global_search",
        )

    with bell_col:
        badge = f'<span class="bell-badge">{unread}</span>' if unread else ""
        st.markdown(f'<div class="topbar-bell">🔔{badge}</div>', unsafe_allow_html=True)

    with user_col:
        st.markdown(
            f"""
            <div class="topbar-user">
                <div class="topbar-avatar">{initials}</div>
                <div>
                    <div class="topbar-name">{user_name}</div>
                    <div class="topbar-role">{role.title()}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )