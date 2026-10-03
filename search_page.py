import pandas as pd
import streamlit as st

from search_service import global_search

DONOR_COLS = {
    "donor_code": "Donor ID", "full_name": "Name", "blood_group": "Group",
    "phone": "Phone", "city": "City",
}
UNIT_COLS = {
    "unit_code": "Unit ID", "donor_name": "Donor", "blood_group": "Group",
    "quantity_ml": "Qty (ml)", "expiry_date": "Expiry", "status": "Status",
    "storage_location": "Location",
}
REQUEST_COLS = {
    "request_code": "Request ID", "patient_name": "Patient",
    "hospital_name": "Hospital", "blood_group": "Group", "units_required": "Units",
    "urgency": "Urgency", "status": "Status",
}


def _clear_search():
    st.session_state["global_search"] = ""


def _section(title, data, columns):
    st.markdown(f"#### {title} ({data['total']})")
    if not data["rows"]:
        st.caption("No matches.")
        return

    df = pd.DataFrame(data["rows"]).rename(columns=columns)[list(columns.values())]
    st.dataframe(df, use_container_width=True, hide_index=True)

    if data["total"] > len(data["rows"]):
        st.caption(
            f"Showing the first {len(data['rows'])} of {data['total']}. "
            "Use that page's own search for the full list."
        )


def render_search_results(query):
    results = global_search(query)

    head, btn = st.columns([5, 1.4], vertical_alignment="center")
    with head:
        st.markdown(f"## Search results for \"{query}\"")
    with btn:
        st.button("✖ Clear search", on_click=_clear_search)
    st.caption("Home / Search")

    if results is None:
        st.info("Type at least 2 letters to search.")
        return

    if all(results[k]["total"] == 0 for k in results):
        st.info("No matches found in donors, units or requests.")
        return

    _section("Donors", results["donors"], DONOR_COLS)
    _section("Blood units", results["units"], UNIT_COLS)
    _section("Requests", results["requests"], REQUEST_COLS)