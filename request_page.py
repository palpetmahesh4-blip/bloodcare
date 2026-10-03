import pandas as pd
import streamlit as st

from request_service import (
    get_requests,
    add_request,
    approve_request,
    reject_request,
    fulfill_request,
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
    "Pending",
    "Approved",
    "Fulfilled",
    "Rejected",
]

URGENCIES = [
    "All",
    "Normal",
    "Urgent",
    "Emergency",
]


# ============================================================
# COMPATIBILITY HELPERS
# ============================================================

def color_status(value):
    """
    Kept for compatibility with older code.
    New table uses native Streamlit components.
    """
    return ""


def color_urgency(value):
    """
    Kept for compatibility with older code.
    New table uses native Streamlit components.
    """
    return ""


STATUS_ICONS = {
    "Pending": "🟡",
    "Approved": "🔵",
    "Fulfilled": "🟢",
    "Rejected": "🔴",
}

URGENCY_ICONS = {
    "Normal": "⚪",
    "Urgent": "🟠",
    "Emergency": "🔴",
}


# ============================================================
# NEW REQUEST DIALOG
# ============================================================

@st.dialog("➕ New Blood Request")
def new_request_dialog():

    with st.form("new_request_form"):

        st.caption(
            "Create a new blood requirement request."
        )

        patient = st.text_input(
            "Patient name",
            placeholder="Example: Ramesh Kadam",
        )

        c1, c2 = st.columns(2)

        with c1:

            age = st.number_input(
                "Patient age",
                min_value=0,
                max_value=120,
                value=30,
                step=1,
            )

        with c2:

            blood_group = st.selectbox(
                "Blood group",
                BLOOD_GROUPS[1:],
            )

        hospital = st.text_input(
            "Hospital",
            placeholder="Example: Ruby Hall Clinic, Pune",
        )

        c3, c4 = st.columns(2)

        with c3:

            units = st.number_input(
                "Units required",
                min_value=1,
                max_value=10,
                value=1,
                step=1,
            )

        with c4:

            urgency = st.selectbox(
                "Urgency",
                URGENCIES[1:],
            )

        submitted = st.form_submit_button(
            "Create Request",
            type="primary",
            width="stretch",
        )

    if submitted:

        try:

            code = add_request(
                patient,
                int(age),
                hospital,
                blood_group,
                int(units),
                urgency,
                st.session_state["user"]["id"],
            )

            log_activity(
                st.session_state["user"]["id"],
                "CREATE_REQUEST",
                f"Created request {code}",
            )

            st.session_state["flash"] = (
                f"Request {code} created successfully"
            )

            st.rerun()

        except ValueError as e:

            st.error(str(e))


def request_summary(rows):

    total = len(rows)

    pending = sum(
        1
        for row in rows
        if row.get("status") == "Pending"
    )

    approved = sum(
        1
        for row in rows
        if row.get("status") == "Approved"
    )

    fulfilled = sum(
        1
        for row in rows
        if row.get("status") == "Fulfilled"
    )

    emergency = sum(
        1
        for row in rows
        if row.get("urgency") == "Emergency"
    )

    cards = st.columns(
        5,
        gap="medium",
    )

    with cards[0]:
        kpi_card(
            "📋",
            total,
            "Total Requests",
            "All blood requests",
            "blue",
            "up",
        )

    with cards[1]:
        kpi_card(
            "🟡",
            pending,
            "Pending",
            "Waiting for approval",
            "amber",
            "warning",
        )

    with cards[2]:
        kpi_card(
            "🔵",
            approved,
            "Approved",
            "Ready for fulfillment",
            "blue",
            "up",
        )

    with cards[3]:
        kpi_card(
            "🟢",
            fulfilled,
            "Fulfilled",
            "Successfully completed",
            "green",
            "up",
        )

    with cards[4]:
        kpi_card(
            "🔴",
            emergency,
            "Emergency",
            "High priority requests",
            "red",
            "warning",
        )

# ============================================================
# RENDER REQUESTS
# ============================================================

def render_requests():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "📋 Blood Requests"
    )

    st.caption(
        "Home / Requests • Manage blood requirements"
    )

    # ========================================================
    # FLASH MESSAGE
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
        [1.6, 5],
        vertical_alignment="center",
    )

    with action_col:

        if st.button(
            "➕ New Request",
            type="primary",
            width="stretch",
        ):

            new_request_dialog()

    with info_col:

        st.caption(
            "Create, review, approve and fulfill "
            "blood requests."
        )

    st.divider()

    # ========================================================
    # FILTERS
    # ========================================================

    st.subheader(
        "Search & Filters"
    )

    f1, f2, f3, f4 = st.columns(
        [3, 1.2, 1.3, 1.3],
        gap="medium",
    )

    with f1:

        search = st.text_input(
            "Search",
            placeholder=(
                "🔍 Search request code, patient or hospital"
            ),
            key="req_search",
        )

    with f2:

        blood_group = st.selectbox(
            "Blood Group",
            BLOOD_GROUPS,
            key="req_group",
        )

    with f3:

        status = st.selectbox(
            "Status",
            STATUSES,
            key="req_status",
        )

    with f4:

        urgency = st.selectbox(
            "Urgency",
            URGENCIES,
            key="req_urgency",
        )

    # ========================================================
    # FETCH REQUESTS
    # ========================================================

    rows = get_requests(
        search,
        blood_group,
        status,
        urgency,
    )

    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not rows:

        st.info(
            "No blood requests found for these filters."
        )

        return

    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        "Request Overview"
    )

    request_summary(rows)

    st.write("")

    # ========================================================
    # PREPARE TABLE
    # ========================================================

    df = pd.DataFrame(
        rows
    ).rename(
        columns={
            "request_code": "Request ID",
            "patient_name": "Patient",
            "patient_age": "Age",
            "hospital_name": "Hospital",
            "blood_group": "Group",
            "units_required": "Units",
            "urgency": "Urgency",
            "status": "Status",
            "request_date": "Date",
        }
    )

    df = df[
        [
            "Request ID",
            "Patient",
            "Age",
            "Hospital",
            "Group",
            "Units",
            "Urgency",
            "Status",
            "Date",
        ]
    ]

    # Add readable icons instead of HTML styling.
    df["Urgency"] = df[
        "Urgency"
    ].apply(
        lambda value: (
            f"{URGENCY_ICONS.get(value, '•')} "
            f"{value}"
        )
    )

    df["Status"] = df[
        "Status"
    ].apply(
        lambda value: (
            f"{STATUS_ICONS.get(value, '•')} "
            f"{value}"
        )
    )

    # ========================================================
    # REQUEST TABLE
    # ========================================================

    st.subheader(
        "Blood Requests"
    )

    st.caption(
        f"Showing {len(df)} request"
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
    # SELECTED REQUEST
    # ========================================================

    selected = event.selection.rows

    if not selected:

        return

    row = rows[selected[0]]

    st.divider()

    st.subheader(
        "Selected Request"
    )

    # ========================================================
    # REQUEST DETAILS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Request ID",
            row["request_code"],
        )

    with c2:

        st.metric(
            "Blood Group",
            row["blood_group"],
        )

    with c3:

        st.metric(
            "Units Required",
            row["units_required"],
        )

    with c4:

        status_icon = STATUS_ICONS.get(
            row["status"],
            "•",
        )

        st.metric(
            "Status",
            f"{status_icon} {row['status']}",
        )

    st.caption(
        f"Patient: {row['patient_name']} • "
        f"Age: {row['patient_age']} • "
        f"Hospital: {row['hospital_name']}"
    )

    urgency_icon = URGENCY_ICONS.get(
        row["urgency"],
        "•",
    )

    st.write(
        f"**Urgency:** {urgency_icon} {row['urgency']}"
    )

    # ========================================================
    # PENDING ACTIONS
    # ========================================================

    if row["status"] == "Pending":

        st.write("")

        st.info(
            "This request is waiting for approval."
        )

        b1, b2, _ = st.columns(
            [1.3, 1.3, 4]
        )

        with b1:

            if st.button(
                "✅ Approve",
                type="primary",
                width="stretch",
            ):

                try:

                    approve_request(
                        row["id"]
                    )

                    log_activity(
                        st.session_state["user"]["id"],
                        "APPROVE_REQUEST",
                        f"Approved request {row['request_code']}",
                    )

                    st.session_state["flash"] = (
                        f"Request {row['request_code']} approved"
                    )

                    st.rerun()

                except ValueError as e:

                    st.error(str(e))

        with b2:

            if st.button(
                "❌ Reject",
                width="stretch",
            ):

                try:

                    reject_request(
                        row["id"]
                    )

                    log_activity(
                        st.session_state["user"]["id"],
                        "REJECT_REQUEST",
                        f"Rejected request {row['request_code']}",
                    )

                    st.session_state["flash"] = (
                        f"Request {row['request_code']} rejected"
                    )

                    st.rerun()

                except ValueError as e:

                    st.error(str(e))

    # ========================================================
    # APPROVED ACTION
    # ========================================================

    elif row["status"] == "Approved":

        st.write("")

        st.info(
            "This request has been approved "
            "and is ready for fulfillment."
        )

        if st.button(
            "🚚 Fulfill Request",
            type="primary",
            width="stretch",
        ):

            try:

                codes = fulfill_request(
                    row["id"],
                    st.session_state["user"]["id"],
                )

                log_activity(
                    st.session_state["user"]["id"],
                    "FULFILL_REQUEST",
                    (
                        f"Fulfilled request "
                        f"{row['request_code']} "
                        f"(units: {', '.join(codes)})"
                    ),
                )

                st.session_state["flash"] = (
                    f"Request {row['request_code']} fulfilled. "
                    f"Issued: {', '.join(codes)}"
                )

                st.rerun()

            except ValueError as e:

                st.error(str(e))

    # ========================================================
    # COMPLETED / REJECTED
    # ========================================================

    else:

        if row["status"] == "Fulfilled":

            st.success(
                "This request has already been fulfilled."
            )

        elif row["status"] == "Rejected":

            st.error(
                "This request has been rejected."
            )

        else:

            st.info(
                f"This request is already "
                f"{row['status']}."
            )