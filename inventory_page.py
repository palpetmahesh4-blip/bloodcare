from datetime import date, timedelta

import pandas as pd
import streamlit as st

from inventory_service import (
    get_inventory,
    get_donors,
    add_unit,
    update_unit,
    delete_unit,
)
from activity_service import log_activity
from ui import kpi_card


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

STATUSES = [
    "All",
    "Available",
    "Reserved",
    "Issued",
    "Expired",
    "Discarded",
]


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================
# donor_page.py imports this function.
# Keep it even though the new inventory table does not
# use HTML-based styling.

def color_status(value):
    styles = {
        "Available": "",
        "Reserved": "",
        "Issued": "",
        "Expired": "",
        "Discarded": "",
    }

    return styles.get(value, "")


# ============================================================
# STATUS ICONS
# ============================================================

STATUS_ICONS = {
    "Available": "🟢",
    "Reserved": "🔵",
    "Issued": "⚪",
    "Expired": "🔴",
    "Discarded": "🟠",
}


# ============================================================
# ADD BLOOD UNIT DIALOG
# ============================================================

@st.dialog("➕ Add Blood Unit")
def add_unit_dialog():

    donors = get_donors()

    if not donors:

        st.warning(
            "No donors are available. Please add a donor first."
        )

        return

    labels = {
        d["id"]: (
            f'{d["donor_code"]} - '
            f'{d["full_name"]} '
            f'({d["blood_group"]})'
        )
        for d in donors
    }

    with st.form("add_unit_form"):

        st.caption(
            "Register a newly collected blood unit."
        )

        donor_id = st.selectbox(
            "Donor",
            list(labels.keys()),
            format_func=lambda i: labels[i],
        )

        c1, c2 = st.columns(2)

        with c1:

            collection = st.date_input(
                "Collection date",
                value=date.today(),
            )

        with c2:

            expiry = st.date_input(
                "Expiry date",
                value=date.today() + timedelta(days=42),
            )

        c3, c4 = st.columns(2)

        with c3:

            qty = st.number_input(
                "Quantity (ml)",
                min_value=100,
                max_value=600,
                value=450,
                step=50,
            )

        with c4:

            status = st.selectbox(
                "Status",
                ["Available", "Reserved"],
            )

        location = st.text_input(
            "Storage location",
            placeholder="Example: Fridge A1",
        )

        submitted = st.form_submit_button(
            "Save Blood Unit",
            type="primary",
            width="stretch",
        )

    if submitted:

        if expiry <= collection:

            st.error(
                "Expiry date must be after collection date."
            )

        elif not location.strip():

            st.error(
                "Please enter a storage location."
            )

        else:

            code = add_unit(
                donor_id,
                qty,
                collection,
                expiry,
                status,
                location.strip(),
            )

            log_activity(
                st.session_state["user"]["id"],
                "ADD_UNIT",
                f"Added blood unit {code}",
            )

            st.session_state["flash"] = (
                f"Unit {code} added successfully"
            )

            st.rerun()


# ============================================================
# EDIT BLOOD UNIT DIALOG
# ============================================================

@st.dialog("✏️ Edit Blood Unit")
def edit_unit_dialog(row):

    st.info(
        f"Unit {row['unit_code']} • "
        f"{row['blood_group']} • "
        f"Donor: {row['donor_name']}"
    )

    statuses = [
        "Available",
        "Reserved",
        "Issued",
        "Expired",
        "Discarded",
    ]

    with st.form("edit_unit_form"):

        c1, c2 = st.columns(2)

        with c1:

            collection = st.date_input(
                "Collection date",
                value=row["collection_date"],
            )

        with c2:

            expiry = st.date_input(
                "Expiry date",
                value=row["expiry_date"],
            )

        c3, c4 = st.columns(2)

        with c3:

            qty = st.number_input(
                "Quantity (ml)",
                min_value=100,
                max_value=600,
                value=int(row["quantity_ml"]),
                step=50,
            )

        with c4:

            status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(
                    row["status"]
                ),
            )

        location = st.text_input(
            "Storage location",
            value=row["storage_location"] or "",
        )

        submitted = st.form_submit_button(
            "Update Blood Unit",
            type="primary",
            width="stretch",
        )

    if submitted:

        if expiry <= collection:

            st.error(
                "Expiry date must be after collection date."
            )

        elif not location.strip():

            st.error(
                "Please enter a storage location."
            )

        else:

            update_unit(
                row["id"],
                qty,
                collection,
                expiry,
                status,
                location.strip(),
            )

            log_activity(
                st.session_state["user"]["id"],
                "EDIT_UNIT",
                f"Edited blood unit {row['unit_code']}",
            )

            st.session_state["flash"] = (
                f"Unit {row['unit_code']} updated successfully"
            )

            st.rerun()


# ============================================================
# DELETE BLOOD UNIT DIALOG
# ============================================================

@st.dialog("🗑️ Delete Blood Unit")
def delete_unit_dialog(row):

    st.warning(
        f"Are you sure you want to delete "
        f"unit {row['unit_code']} "
        f"({row['blood_group']})?"
    )

    st.caption(
        "This action cannot be undone."
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Yes, Delete",
            type="primary",
            width="stretch",
            key="confirm_delete",
        ):

            try:

                delete_unit(
                    row["id"]
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "DELETE_UNIT",
                    f"Deleted blood unit {row['unit_code']}",
                )

                st.session_state["flash"] = (
                    f"Unit {row['unit_code']} deleted"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

    with c2:

        if st.button(
            "Cancel",
            width="stretch",
            key="cancel_delete",
        ):

            st.rerun()


def inventory_summary(rows):

    total = len(rows)

    available = sum(
        1
        for row in rows
        if row.get("status") == "Available"
    )

    reserved = sum(
        1
        for row in rows
        if row.get("status") == "Reserved"
    )

    expired = sum(
        1
        for row in rows
        if row.get("status") == "Expired"
    )

    row1 = st.columns(
        4,
        gap="medium",
    )

    with row1[0]:

        kpi_card(
            "🩸",
            total,
            "Total Blood Units",
            "All units in inventory",
            "red",
            "up",
        )

    with row1[1]:

        kpi_card(
            "✅",
            available,
            "Available Units",
            "Ready to issue",
            "green",
            "up",
        )

    with row1[2]:

        kpi_card(
            "🔵",
            reserved,
            "Reserved Units",
            "Currently reserved",
            "blue",
            "up",
        )

    with row1[3]:

        kpi_card(
            "🔴",
            expired,
            "Expired Units",
            "Need attention",
            "red",
            "warning",
        )

# ============================================================
# INVENTORY PAGE
# ============================================================

def render_inventory():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "🩸 Blood Inventory"
    )

    st.caption(
        "Home / Inventory • Manage and monitor blood stock"
    )

    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    if "flash" in st.session_state:

        st.toast(
            st.session_state.pop("flash"),
            icon="✅",
        )

    # ========================================================
    # ACTION BAR
    # ========================================================

    action_col, info_col = st.columns(
        [1.5, 5],
        vertical_alignment="center",
    )

    with action_col:

        if st.button(
            "➕ Add Blood Unit",
            type="primary",
            width="stretch",
        ):

            add_unit_dialog()

    with info_col:

        st.caption(
            "Track collected units, storage locations, "
            "expiry dates and availability."
        )

    st.divider()

    # ========================================================
    # SEARCH & FILTERS
    # ========================================================

    st.subheader(
        "Search & Filters"
    )

    f1, f2, f3 = st.columns(
        [3, 1.3, 1.3],
        gap="medium",
    )

    with f1:

        search = st.text_input(
            "Search",
            placeholder=(
                "🔍 Search unit code or donor name"
            ),
            key="inv_search",
        )

    with f2:

        blood_group = st.selectbox(
            "Blood Group",
            BLOOD_GROUPS,
            key="inv_group",
        )

    with f3:

        status = st.selectbox(
            "Status",
            STATUSES,
            key="inv_status",
        )

    # ========================================================
    # GET INVENTORY
    # ========================================================

    rows = get_inventory(
        search,
        blood_group,
        status,
    )

    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not rows:

        st.info(
            "No blood units found for these filters."
        )

        return

    # ========================================================
    # INVENTORY OVERVIEW
    # ========================================================

    st.subheader(
        "Inventory Overview"
    )

    inventory_summary(rows)

    st.write("")

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(rows).rename(
        columns={
            "unit_code": "Unit ID",
            "donor_name": "Donor",
            "blood_group": "Group",
            "quantity_ml": "Qty (ml)",
            "collection_date": "Collected",
            "expiry_date": "Expiry",
            "status": "Status",
            "storage_location": "Location",
        }
    )

    if "id" in df.columns:

        df = df.drop(
            columns=["id"]
        )

    # ========================================================
    # STATUS DISPLAY
    # ========================================================

    if "Status" in df.columns:

        df["Status"] = df["Status"].apply(
            lambda value: (
                f"{STATUS_ICONS.get(value, '•')} "
                f"{value}"
            )
        )

    # ========================================================
    # STOCK TABLE
    # ========================================================

    st.subheader(
        "Blood Stock"
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
    # SELECTED ROW
    # ========================================================

    selected = event.selection.rows

    if selected:

        row = rows[selected[0]]

        st.divider()

        st.subheader(
            "Selected Unit"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Unit ID",
                row["unit_code"],
            )

        with c2:

            st.metric(
                "Blood Group",
                row["blood_group"],
            )

        with c3:

            st.metric(
                "Quantity",
                f'{row["quantity_ml"]} ml',
            )

        with c4:

            icon = STATUS_ICONS.get(
                row["status"],
                "•",
            )

            st.metric(
                "Status",
                f"{icon} {row['status']}",
            )

        st.caption(
            f"Donor: {row['donor_name']} • "
            f"Location: {row['storage_location']}"
        )

        edit_col, delete_col, _ = st.columns(
            [1.5, 1.5, 4]
        )

        with edit_col:

            if st.button(
                "✏️ Edit Unit",
                width="stretch",
            ):

                edit_unit_dialog(row)

        with delete_col:

            if st.button(
                "🗑️ Delete Unit",
                width="stretch",
            ):

                delete_unit_dialog(row)