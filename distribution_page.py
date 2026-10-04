import pandas as pd
import streamlit as st

from distribution_service import get_distributions
from ui import kpi_card



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


STATUS_ICONS = {
    "Completed": "🟢",
    "Pending": "🟡",
    "Cancelled": "🔴",
}




def color_dist_status(value):
    """
    Kept for compatibility with older code.
    New table uses native Streamlit formatting.
    """
    return ""



def render_distribution():


    st.title(
        "🚚 Blood Distribution"
    )

    st.caption(
        "Home / Distribution • Track issued blood units"
    )

    st.divider()

   

    st.subheader(
        "Search & Filters"
    )

    f1, f2 = st.columns(
        [4, 1.4],
        gap="medium",
    )

    with f1:

        search = st.text_input(
            "Search",
            placeholder=(
                "🔍 Search distribution code, unit, "
                "patient, hospital or request"
            ),
            key="dist_search",
        )

    with f2:

        blood_group = st.selectbox(
            "Blood Group",
            BLOOD_GROUPS,
            key="dist_group",
        )


    rows = get_distributions(
        search,
        blood_group,
    )

 

    if not rows:

        st.info(
            "No distribution records found for these filters."
        )

        return

 

    total_units = len(rows)

    total_litres = round(
        sum(
            r["quantity_ml"]
            for r in rows
        ) / 1000,
        2,
    )

    hospitals = len(
        {
            r["hospital_name"]
            for r in rows
        }
    )

    completed = sum(
        1
        for r in rows
        if r.get("status") == "Completed"
    )

  

    st.subheader(
        "Distribution Overview"
    )

    cards = st.columns(
        4,
        gap="medium",
    )

    with cards[0]:

        kpi_card(
            "🚚",
            total_units,
            "Units Issued",
            "Matching your filters",
            "red",
            "up",
        )

    with cards[1]:

        kpi_card(
            "🩸",
            f"{total_litres} L",
            "Blood Distributed",
            "Total volume issued",
            "blue",
            "up",
        )

    with cards[2]:

        kpi_card(
            "🏥",
            hospitals,
            "Hospitals Served",
            "Unique hospitals",
            "green",
            "up",
        )

    with cards[3]:

        kpi_card(
            "✅",
            completed,
            "Completed",
            "Successfully distributed",
            "green",
            "up",
        )

    st.write("")



    st.subheader(
        "Distribution Records"
    )

    df = pd.DataFrame(
        rows
    ).rename(
        columns={
            "distribution_code": "Dist ID",
            "request_code": "Request",
            "unit_code": "Unit",
            "blood_group": "Group",
            "quantity_ml": "Qty (ml)",
            "hospital_name": "Hospital",
            "patient_name": "Patient",
            "issue_date": "Issue date",
            "issued_by_name": "Issued by",
            "status": "Status",
        }
    )

    df = df[
        [
            "Dist ID",
            "Request",
            "Unit",
            "Group",
            "Qty (ml)",
            "Hospital",
            "Patient",
            "Issue date",
            "Issued by",
            "Status",
        ]
    ]

    # Add readable status icons.
    df["Status"] = df[
        "Status"
    ].apply(
        lambda value: (
            f"{STATUS_ICONS.get(value, '•')} "
            f"{value}"
        )
    )

    st.caption(
        f"Showing {len(df)} distribution record"
        f"{'s' if len(df) != 1 else ''}"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )