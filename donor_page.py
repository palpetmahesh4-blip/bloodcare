from datetime import date

import pandas as pd
import streamlit as st

from donor_service import (
    get_donor_list,
    add_donor,
    update_donor,
    delete_donor,
    get_donor_history,
)
from inventory_page import color_status
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

ELIGIBILITY = [
    "All",
    "Eligible",
    "Not eligible",
]

GENDERS = [
    "Male",
    "Female",
    "Other",
]
STATUS_ICONS = {
    "Available": "🟢",
    "Reserved": "🔵",
    "Issued": "⚪",
    "Expired": "🔴",
    "Discarded": "🟠",
}


# ============================================================
# ELIGIBILITY HELPER
# ============================================================

def color_eligibility(value):
    """
    Compatibility helper.

    Kept because older parts of the project may import it.
    No HTML styling is used in the new donor table.
    """

    styles = {
        "Eligible": "",
        "Not eligible": "",
    }

    return styles.get(value, "")


# ============================================================
# ADD DONOR
# ============================================================

@st.dialog("➕ Add Donor")
def add_donor_dialog():

    with st.form("add_donor_form"):

        st.caption(
            "Register a new blood donor."
        )

        full_name = st.text_input(
            "Full name",
            placeholder="Example: Rahul Deshmukh",
        )

        c1, c2 = st.columns(2)

        with c1:

            gender = st.selectbox(
                "Gender",
                GENDERS,
            )

        with c2:

            blood_group = st.selectbox(
                "Blood group",
                BLOOD_GROUPS[1:],
            )

        c3, c4 = st.columns(2)

        with c3:

            dob = st.date_input(
                "Date of birth",
                value=date(2000, 1, 1),
                min_value=date(1950, 1, 1),
                max_value=date.today(),
            )

        with c4:

            phone = st.text_input(
                "Phone",
                max_chars=10,
                placeholder="10 digit mobile number",
            )

        c5, c6 = st.columns(2)

        with c5:

            email = st.text_input(
                "Email",
                placeholder="Optional",
            )

        with c6:

            city = st.text_input(
                "City",
                placeholder="Example: Mumbai",
            )

        last_donation = st.date_input(
            "Last donation date",
            value=None,
            max_value=date.today(),
        )

        eligible = st.checkbox(
            "Eligible to donate",
            value=True,
        )

        submitted = st.form_submit_button(
            "Save Donor",
            type="primary",
            width="stretch",
        )

    if submitted:

        if not full_name.strip():

            st.error(
                "Please enter the donor's name."
            )

        elif not city.strip():

            st.error(
                "Please enter the city."
            )

        else:

            try:

                code = add_donor(
                    full_name,
                    gender,
                    dob,
                    blood_group,
                    phone,
                    email,
                    city,
                    last_donation,
                    eligible,
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "ADD_DONOR",
                    f"Added donor {code}",
                )

                st.session_state["flash"] = (
                    f"Donor {code} added successfully"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))


# ============================================================
# EDIT DONOR
# ============================================================

@st.dialog("✏️ Edit Donor")
def edit_donor_dialog(row):

    groups = BLOOD_GROUPS[1:]

    with st.form("edit_donor_form"):

        st.caption(
            f"Editing donor {row['donor_code']}"
        )

        full_name = st.text_input(
            "Full name",
            value=row["full_name"],
        )

        c1, c2 = st.columns(2)

        with c1:

            gender = st.selectbox(
                "Gender",
                GENDERS,
                index=GENDERS.index(
                    row["gender"]
                ),
            )

        with c2:

            blood_group = st.selectbox(
                "Blood group",
                groups,
                index=groups.index(
                    row["blood_group"]
                ),
            )

        c3, c4 = st.columns(2)

        with c3:

            dob = st.date_input(
                "Date of birth",
                value=row["date_of_birth"],
                min_value=date(1950, 1, 1),
                max_value=date.today(),
            )

        with c4:

            phone = st.text_input(
                "Phone",
                value=row["phone"],
                max_chars=10,
            )

        c5, c6 = st.columns(2)

        with c5:

            email = st.text_input(
                "Email",
                value=row["email"] or "",
            )

        with c6:

            city = st.text_input(
                "City",
                value=row["city"],
            )

        last_donation = st.date_input(
            "Last donation date",
            value=row["last_donation_date"],
            max_value=date.today(),
        )

        eligible = st.checkbox(
            "Eligible to donate",
            value=bool(row["is_eligible"]),
        )

        submitted = st.form_submit_button(
            "Update Donor",
            type="primary",
            width="stretch",
        )

    if submitted:

        if not full_name.strip():

            st.error(
                "Please enter the donor's name."
            )

        elif not city.strip():

            st.error(
                "Please enter the city."
            )

        else:

            try:

                update_donor(
                    row["id"],
                    full_name,
                    gender,
                    dob,
                    blood_group,
                    phone,
                    email,
                    city,
                    last_donation,
                    eligible,
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "EDIT_DONOR",
                    f"Edited donor {row['donor_code']}",
                )

                st.session_state["flash"] = (
                    f"Donor {row['donor_code']} updated successfully"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))


# ============================================================
# DELETE DONOR
# ============================================================

@st.dialog("🗑️ Delete Donor")
def delete_donor_dialog(row):

    st.warning(
        f"Are you sure you want to delete "
        f"donor {row['donor_code']} - "
        f"{row['full_name']}?"
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
            key="confirm_delete_donor",
        ):

            try:

                delete_donor(
                    row["id"]
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "DELETE_DONOR",
                    f"Deleted donor {row['donor_code']}",
                )

                st.session_state["flash"] = (
                    f"Donor {row['donor_code']} deleted"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

    with c2:

        if st.button(
            "Cancel",
            width="stretch",
            key="cancel_delete_donor",
        ):

            st.rerun()


def donor_summary(rows):

    total = len(rows)

    eligible = sum(
        1
        for row in rows
        if bool(row.get("is_eligible"))
    )

    not_eligible = total - eligible

    total_units = sum(
        int(row.get("units_donated") or 0)
        for row in rows
    )

    cards = st.columns(
        4,
        gap="medium",
    )

    with cards[0]:
        kpi_card(
            "👥",
            total,
            "Total Donors",
            "Registered donors",
            "blue",
            "up",
        )

    with cards[1]:
        kpi_card(
            "🟢",
            eligible,
            "Eligible Donors",
            "Ready to donate",
            "green",
            "up",
        )

    with cards[2]:
        kpi_card(
            "🔴",
            not_eligible,
            "Not Eligible",
            "Currently unavailable",
            "red",
            "warning",
        )

    with cards[3]:
        kpi_card(
            "🩸",
            total_units,
            "Units Donated",
            "Total donations recorded",
            "red",
            "up",
        )


# ============================================================
# DONOR PAGE
# ============================================================

def render_donors():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "👥 Donor Management"
    )

    st.caption(
        "Home / Donors • Manage registered blood donors"
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
    # ACTION BAR
    # ========================================================

    action_col, info_col = st.columns(
        [1.5, 5],
        vertical_alignment="center",
    )

    with action_col:

        if st.button(
            "➕ Add Donor",
            type="primary",
            width="stretch",
        ):

            add_donor_dialog()

    with info_col:

        st.caption(
            "Manage donor profiles, eligibility, "
            "blood groups and donation history."
        )

    st.divider()

    # ========================================================
    # FILTERS
    # ========================================================

    st.subheader(
        "Search & Filters"
    )

    f1, f2, f3 = st.columns(
        [3, 1.3, 1.5],
        gap="medium",
    )

    with f1:

        search = st.text_input(
            "Search",
            placeholder=(
                "🔍 Search name, donor code or phone"
            ),
            key="donor_search",
        )

    with f2:

        blood_group = st.selectbox(
            "Blood Group",
            BLOOD_GROUPS,
            key="donor_group",
        )

    with f3:

        eligibility = st.selectbox(
            "Eligibility",
            ELIGIBILITY,
            key="donor_eligibility",
        )

    # ========================================================
    # GET DONORS
    # ========================================================

    rows = get_donor_list(
        search,
        blood_group,
        eligibility,
    )

    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not rows:

        st.info(
            "No donors found for these filters."
        )

        return

    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        "Donor Overview"
    )

    donor_summary(rows)

    st.write("")

    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(rows)

    df["Eligibility"] = df[
        "is_eligible"
    ].map(
        {
            1: "🟢 Eligible",
            0: "🔴 Not eligible",
            True: "🟢 Eligible",
            False: "🔴 Not eligible",
        }
    )

    df = df.rename(
        columns={
            "donor_code": "Donor ID",
            "full_name": "Name",
            "gender": "Gender",
            "blood_group": "Group",
            "phone": "Phone",
            "city": "City",
            "last_donation_date": "Last donation",
            "units_donated": "Units donated",
        }
    )

    df = df[
        [
            "Donor ID",
            "Name",
            "Gender",
            "Group",
            "Phone",
            "City",
            "Last donation",
            "Units donated",
            "Eligibility",
        ]
    ]

    # ========================================================
    # TABLE
    # ========================================================

    st.subheader(
        "Registered Donors"
    )

    st.caption(
        f"Showing {len(df)} donor"
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
    # SELECTED DONOR
    # ========================================================

    selected = event.selection.rows

    if selected:

        row = rows[selected[0]]

        st.divider()

        st.subheader(
            "Selected Donor"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Donor ID",
                row["donor_code"],
            )

        with c2:

            st.metric(
                "Blood Group",
                row["blood_group"],
            )

        with c3:

            st.metric(
                "Units Donated",
                row["units_donated"] or 0,
            )

        with c4:

            if bool(row["is_eligible"]):

                st.metric(
                    "Eligibility",
                    "🟢 Eligible",
                )

            else:

                st.metric(
                    "Eligibility",
                    "🔴 Not eligible",
                )

        st.caption(
            f"Name: {row['full_name']} • "
            f"Phone: {row['phone']} • "
            f"City: {row['city']}"
        )

        # ====================================================
        # ACTIONS
        # ====================================================

        b1, b2, _ = st.columns(
            [1.5, 1.5, 4]
        )

        with b1:

            if st.button(
                "✏️ Edit Donor",
                width="stretch",
            ):

                edit_donor_dialog(row)

        with b2:

            if st.button(
                "🗑️ Delete Donor",
                width="stretch",
            ):

                delete_donor_dialog(row)

        # ====================================================
        # DONATION HISTORY
        # ====================================================

        st.subheader(
            "Donation History"
        )

        history = get_donor_history(
            row["id"]
        )

        if history:

            hdf = pd.DataFrame(
                history
            ).rename(
                columns={
                    "unit_code": "Unit ID",
                    "blood_group": "Group",
                    "quantity_ml": "Qty (ml)",
                    "collection_date": "Collected",
                    "expiry_date": "Expiry",
                    "status": "Status",
                }
            )

            if "Status" in hdf.columns:

                hdf["Status"] = hdf[
                    "Status"
                ].apply(
                    lambda value: (
                        f"{STATUS_ICONS.get(value, '•')} "
                        f"{value}"
                    )
                )

            st.dataframe(
                hdf,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No donations recorded for this donor yet."
            )