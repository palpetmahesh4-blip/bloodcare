import pandas as pd
import streamlit as st

from expiry_service import (
    get_expiry_units,
    discard_unit,
)
from ui import kpi_card
from activity_service import log_activity


# ============================================================
# CONSTANTS
# ============================================================

BLOOD_GROUPS = [
    "All",
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "O+",
    "O-",
]

BUCKET_FILTERS = [
    "All",
    "Expired",
    "Expires today",
    "Within 7 days",
    "Within 30 days",
    "Safe",
]


BUCKET_ICONS = {
    "Expired": "🔴",
    "Expires today": "🔴",
    "Within 7 days": "🟠",
    "Within 30 days": "🔵",
    "Safe": "🟢",
}


STOCK_ICONS = {
    "Available": "🟢",
    "Reserved": "🔵",
    "Issued": "⚪",
    "Expired": "🔴",
    "Discarded": "🟠",
}


# ============================================================
# COMPATIBILITY HELPER
# ============================================================

def color_bucket(value):
    """
    Kept for compatibility with older code.
    New table uses native Streamlit formatting.
    """
    return ""


# ============================================================
# DISCARD DIALOG
# ============================================================

@st.dialog("🗑️ Discard Blood Unit")
def discard_dialog(unit):

    st.warning(
        f"Are you sure you want to discard unit "
        f"{unit['unit_code']}?"
    )

    st.caption(
        f"Blood group: {unit['blood_group']} • "
        f"Expired on: {unit['expiry_date']}"
    )

    st.caption(
        "This action cannot be undone."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Yes, Discard",
            type="primary",
            width="stretch",
            key="confirm_discard",
        ):

            try:

                code = discard_unit(
                    unit["id"]
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "DISCARD_UNIT",
                    f"Discarded unit {code}",
                )

                st.session_state["flash"] = (
                    f"Unit {code} discarded"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

    with c2:

        if st.button(
            "Cancel",
            width="stretch",
            key="cancel_discard",
        ):

            st.rerun()


# ============================================================
# EXPIRY PAGE
# ============================================================

def render_expiry():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "⏳ Expiry Management"
    )

    st.caption(
        "Home / Expiry • Monitor blood unit expiry"
    )

    # ========================================================
    # FLASH
    # ========================================================

    if "flash" in st.session_state:

        st.toast(
            st.session_state.pop("flash"),
            icon="✅",
        )

    # ========================================================
    # GET ALL UNITS
    # ========================================================

    all_units = get_expiry_units()

    def count(bucket):

        return sum(
            1
            for unit in all_units
            if unit["bucket"] == bucket
        )

    # ========================================================
    # KPI CARDS
    # ========================================================

    st.subheader(
        "Expiry Overview"
    )

    cards = st.columns(
        4,
        gap="medium",
    )

    with cards[0]:

        kpi_card(
            "⛔",
            count("Expired"),
            "Already Expired",
            "Needs discarding",
            "red",
            "down",
        )

    with cards[1]:

        kpi_card(
            "🔥",
            count("Expires today"),
            "Expires Today",
            "Requires immediate attention",
            "red",
            "down",
        )

    with cards[2]:

        kpi_card(
            "⏳",
            count("Within 7 days"),
            "Within 7 Days",
            "Use soon",
            "amber",
            "warning",
        )

    with cards[3]:

        kpi_card(
            "📅",
            count("Within 30 days"),
            "Within 30 Days",
            "Plan ahead",
            "blue",
            "up",
        )

    st.write("")

    # ========================================================
    # FILTERS
    # ========================================================

    st.subheader(
        "Search & Filters"
    )

    f1, f2, _ = st.columns(
        [1.6, 1.3, 3],
        gap="medium",
    )

    with f1:

        bucket = st.selectbox(
            "Expiry Status",
            BUCKET_FILTERS,
            key="exp_bucket",
        )

    with f2:

        blood_group = st.selectbox(
            "Blood Group",
            BLOOD_GROUPS,
            key="exp_group",
        )

    # ========================================================
    # FILTERED UNITS
    # ========================================================

    units = get_expiry_units(
        bucket,
        blood_group,
    )

    if not units:

        st.info(
            "No blood units found for these filters."
        )

        return

    # ========================================================
    # TABLE DATA
    # ========================================================

    df = pd.DataFrame(
        units
    ).rename(
        columns={
            "unit_code": "Unit ID",
            "blood_group": "Group",
            "quantity_ml": "Qty (ml)",
            "expiry_date": "Expiry date",
            "days_left": "Days left",
            "bucket": "Expiry status",
            "status": "Stock status",
            "storage_location": "Location",
        }
    )

    df = df[
        [
            "Unit ID",
            "Group",
            "Qty (ml)",
            "Expiry date",
            "Days left",
            "Expiry status",
            "Stock status",
            "Location",
        ]
    ]

    # ========================================================
    # READABLE STATUS
    # ========================================================

    df["Expiry status"] = df[
        "Expiry status"
    ].apply(
        lambda value: (
            f"{BUCKET_ICONS.get(value, '•')} "
            f"{value}"
        )
    )

    df["Stock status"] = df[
        "Stock status"
    ].apply(
        lambda value: (
            f"{STOCK_ICONS.get(value, '•')} "
            f"{value}"
        )
    )

    # ========================================================
    # TABLE
    # ========================================================

    st.subheader(
        "Expiry Records"
    )

    st.caption(
        f"Showing {len(df)} blood unit"
        f"{'s' if len(df) != 1 else ''}"
    )

    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # ========================================================
    # SELECTED UNIT
    # ========================================================

    selected = event.selection.rows

    if not selected:

        return

    unit = units[selected[0]]

    st.divider()

    st.subheader(
        "Selected Blood Unit"
    )

    # ========================================================
    # UNIT DETAILS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Unit ID",
            unit["unit_code"],
        )

    with c2:

        st.metric(
            "Blood Group",
            unit["blood_group"],
        )

    with c3:

        st.metric(
            "Quantity",
            f'{unit["quantity_ml"]} ml',
        )

    with c4:

        st.metric(
            "Days Left",
            unit["days_left"],
        )

    st.caption(
        f"Expiry: {unit['expiry_date']} • "
        f"Location: {unit['storage_location']}"
    )

    # ========================================================
    # DISCARD ACTION
    # ========================================================

    if unit["bucket"] == "Expired":

        st.error(
            "This blood unit has expired and should be discarded."
        )

        if st.button(
            "🗑️ Discard Unit",
            type="primary",
        ):

            discard_dialog(unit)

    else:

        st.info(
            "Only expired units can be discarded."
        )