from datetime import date, timedelta

import pandas as pd
import streamlit as st

from print_view import render_print_view
from report_service import (
    inventory_report,
    donor_report,
    request_report,
    distribution_report,
    expiry_report,
)
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


REPORTS = {
    "Inventory report": (
        inventory_report,
        "inventory_report",
        "Filtered by collection date",
    ),
    "Donor report": (
        donor_report,
        "donor_report",
        "Filtered by donor registration date",
    ),
    "Blood request report": (
        request_report,
        "request_report",
        "Filtered by request date",
    ),
    "Distribution report": (
        distribution_report,
        "distribution_report",
        "Filtered by issue date",
    ),
    "Expiry report": (
        expiry_report,
        "expiry_report",
        "Filtered by expiry date",
    ),
}


# ============================================================
# REPORT KPI
# ============================================================

def report_summary(df, report_name):

    total_records = len(df)

    cards = st.columns(
        4,
        gap="medium",
    )

    with cards[0]:

        kpi_card(
            "📊",
            total_records,
            "Total Records",
            "Records matching filters",
            "blue",
            "up",
        )

    with cards[1]:

        kpi_card(
            "📋",
            report_name.replace(
                " report",
                "",
            ),
            "Report Type",
            "Currently selected",
            "red",
            "up",
        )

    with cards[2]:

        if "blood_group" in df.columns:

            groups = df["blood_group"].nunique()

            kpi_card(
                "🩸",
                groups,
                "Blood Groups",
                "Groups in report",
                "red",
                "up",
            )

        else:

            kpi_card(
                "📅",
                "Filtered",
                "Date Range",
                "Report period applied",
                "blue",
                "up",
            )

    with cards[3]:

        kpi_card(
            "📄",
            "CSV",
            "Export Available",
            "Download report data",
            "green",
            "up",
        )


# ============================================================
# REPORT PAGE
# ============================================================

def render_reports():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "📑 Reports"
    )

    st.caption(
        "Home / Reports • Generate and export management reports"
    )

    # ========================================================
    # FILTER SECTION
    # ========================================================

    st.subheader(
        "Report Filters"
    )

    with st.container(border=True):

        f1, f2, f3, f4 = st.columns(
            [1.8, 1.2, 1.2, 1.2],
            gap="medium",
        )

        with f1:

            report_name = st.selectbox(
                "Report",
                list(REPORTS.keys()),
                key="rep_type",
            )

        with f2:

            date_from = st.date_input(
                "From",
                value=(
                    date.today()
                    - timedelta(days=365)
                ),
                key="rep_from",
            )

        with f3:

            date_to = st.date_input(
                "To",
                value=(
                    date.today()
                    + timedelta(days=90)
                ),
                key="rep_to",
            )

        with f4:

            blood_group = st.selectbox(
                "Blood Group",
                BLOOD_GROUPS,
                key="rep_group",
            )

    # ========================================================
    # REPORT CONFIG
    # ========================================================

    run_report, file_prefix, date_note = REPORTS[
        report_name
    ]

    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if date_from > date_to:

        st.error(
            "'From' date must be before 'To' date."
        )

        return

    # ========================================================
    # GENERATE REPORT
    # ========================================================

    df = run_report(
        date_from,
        date_to,
        blood_group,
    )

    # ========================================================
    # EMPTY STATE
    # ========================================================

    if df.empty:

        st.info(
            "No records found for these filters."
        )

        return

    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader(
        "Report Overview"
    )

    report_summary(
        df,
        report_name,
    )

    st.write("")

    # ========================================================
    # EXPORT BAR
    # ========================================================

    info_col, btn_col = st.columns(
        [4, 1.4],
        vertical_alignment="center",
    )

    with info_col:

        st.caption(
            f"{len(df)} records • {date_note}"
        )

        st.caption(
            f"Period: "
            f"{date_from.strftime('%d %b %Y')} "
            f"→ "
            f"{date_to.strftime('%d %b %Y')} "
            f"• Blood group: {blood_group}"
        )

    with btn_col:

        csv_bytes = (
            df
            .to_csv(index=False)
            .encode("utf-8-sig")
        )

        file_name = (
            f"{file_prefix}_"
            f"{date.today().isoformat()}.csv"
        )

        st.download_button(
            "⬇️ Download CSV",
            data=csv_bytes,
            file_name=file_name,
            mime="text/csv",
            type="primary",
            width="stretch",
        )

    st.divider()

    # ========================================================
    # REPORT CONTENT
    # ========================================================

    tab_table, tab_print = st.tabs(
        [
            "📋 Report Table",
            "🖨️ Print View",
        ]
    )

    # ========================================================
    # TABLE
    # ========================================================

    with tab_table:

        st.subheader(
            report_name
        )

        st.caption(
            "Review the generated report data below."
        )

        display_df = df.copy()

        # Convert date/datetime columns into
        # readable values without changing
        # the original report dataframe.

        for column in display_df.columns:

            if (
                pd.api.types.is_datetime64_any_dtype(
                    display_df[column]
                )
            ):

                display_df[column] = (
                    display_df[column]
                    .dt.strftime("%d %b %Y")
                )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # PRINT VIEW
    # ========================================================

    with tab_print:

        st.subheader(
            "Print View"
        )

        st.caption(
            "Use the print layout for a clean report copy."
        )

        render_print_view(
            df,
            report_name,
            date_from,
            date_to,
            blood_group,
        )