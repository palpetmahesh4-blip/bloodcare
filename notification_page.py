import streamlit as st

from notification_service import (
    sync_alerts, get_notifications, mark_all_read,
)

CATEGORIES = ["All", "stock", "expiry", "request"]
CATEGORY_LABELS = {
    "All": "All",
    "stock": "Low stock",
    "expiry": "Expiry",
    "request": "Requests",
}
SEVERITY_ICON = {"danger": "🔴", "warning": "🟡", "info": "🔵"}


def render_notifications():
    st.markdown("## Notifications")
    st.caption("Home / Notifications")

    sync_alerts()

    if "flash" in st.session_state:
        st.toast(st.session_state.pop("flash"), icon="✅")

    f1, f2, f3 = st.columns([1.6, 1.4, 1.4], vertical_alignment="bottom")
    with f1:
        category = st.selectbox(
            "Category",
            CATEGORIES,
            format_func=lambda c: CATEGORY_LABELS[c],
            key="notif_category",
        )
    with f2:
        only_unread = st.checkbox("Unread only", key="notif_unread")
    with f3:
        if st.button("Mark all as read"):
            mark_all_read()
            st.session_state["flash"] = "All notifications marked as read"
            st.rerun()

    items = get_notifications(category, only_unread)

    if not items:
        st.info("No notifications to show.")
        return

    st.caption(f"{len(items)} notifications")

    for n in items:
        icon = SEVERITY_ICON.get(n["severity"], "🔵")
        with st.container(border=True):
            title = f"{icon} **{n['title']}**"
            if not n["is_read"]:
                title += "  `NEW`"
            st.markdown(title)
            st.write(n["message"])
            st.caption(n["created_at"].strftime("%d %b %Y, %I:%M %p"))