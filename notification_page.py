
import streamlit as st

from datetime import datetime

from notification_service import (
    sync_alerts,
    get_notifications,
    mark_all_read,
)


CATEGORIES = [
    "All",
    "stock",
    "expiry",
    "request",
]

CATEGORY_LABELS = {
    "All": "All",
    "stock": "Low stock",
    "expiry": "Expiry",
    "request": "Requests",
}

SEVERITY_ICON = {
    "danger": "🔴",
    "warning": "🟡",
    "info": "🔵",
}


# ============================================================
# DATE/TIME FORMATTER
# ============================================================

def format_notification_time(value):
    """
    SQLite normally returns DateTime values as strings.
    This function supports both SQLite strings and
    Python datetime objects.
    """

    if value is None:
        return ""

    # Already a datetime object
    if isinstance(value, datetime):
        return value.strftime(
            "%d %b %Y, %I:%M %p"
        )

    # SQLite returns a string
    if isinstance(value, str):

        value = value.strip()

        # Try common SQLite datetime formats
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)

                return dt.strftime(
                    "%d %b %Y, %I:%M %p"
                )

            except ValueError:
                continue

        # If SQLite gives an unexpected format,
        # show the original value instead of crashing.
        return value

    # Safe fallback
    return str(value)


# ============================================================
# NOTIFICATIONS PAGE
# ============================================================

def render_notifications():

    st.markdown("## Notifications")
    st.caption("Home / Notifications")

    # --------------------------------------------------------
    # SYNC CURRENT ALERTS
    # --------------------------------------------------------

    sync_alerts()

    # --------------------------------------------------------
    # FLASH MESSAGE
    # --------------------------------------------------------

    if "flash" in st.session_state:

        st.toast(
            st.session_state.pop("flash"),
            icon="✅"
        )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    f1, f2, f3 = st.columns(
        [1.6, 1.4, 1.4],
        vertical_alignment="bottom"
    )

    with f1:

        category = st.selectbox(
            "Category",
            CATEGORIES,
            format_func=lambda c: CATEGORY_LABELS[c],
            key="notif_category",
        )

    with f2:

        only_unread = st.checkbox(
            "Unread only",
            key="notif_unread"
        )

    with f3:

        if st.button(
            "Mark all as read",
            use_container_width=True
        ):

            mark_all_read()

            st.session_state["flash"] = (
                "All notifications marked as read"
            )

            st.rerun()

    # --------------------------------------------------------
    # FETCH NOTIFICATIONS
    # --------------------------------------------------------

    items = get_notifications(
        category,
        only_unread
    )

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not items:

        st.info(
            "No notifications to show."
        )

        return

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    st.caption(
        f"{len(items)} notifications"
    )

    # --------------------------------------------------------
    # NOTIFICATION CARDS
    # --------------------------------------------------------

    for n in items:

        icon = SEVERITY_ICON.get(
            n["severity"],
            "🔵"
        )

        with st.container(border=True):

            title = (
                f"{icon} **{n['title']}**"
            )

            if not n["is_read"]:

                title += "  `NEW`"

            st.markdown(title)

            st.write(
                n["message"]
            )

            # SQLite-safe date formatting
            st.caption(
                format_notification_time(
                    n["created_at"]
                )
            )

