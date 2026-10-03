import streamlit as st

from activity_service import get_recent_activity
from queries import get_kpis
from chart_service import (
    get_stock_by_group,
    get_monthly_collection,
    get_request_status_counts,
    get_expiry_overview,
)
from charts import (
    stock_chart,
    monthly_chart,
    request_chart,
    expiry_chart,
)
from ui import kpi_card


# ============================================================
# CONFIG
# ============================================================

CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


# ============================================================
# ACTIVITY ICONS
# ============================================================

ACTION_ICONS = {
    "LOGIN": "🔑",
    "LOGOUT": "🚪",
    "ADD_UNIT": "🩸",
    "EDIT_UNIT": "✏️",
    "DELETE_UNIT": "🗑️",
    "DISCARD_UNIT": "🗑️",
    "ADD_DONOR": "👤",
    "EDIT_DONOR": "✏️",
    "DELETE_DONOR": "🗑️",
    "CREATE_REQUEST": "📋",
    "APPROVE_REQUEST": "✅",
    "REJECT_REQUEST": "❌",
    "FULFILL_REQUEST": "🚚",
    "ISSUE_BLOOD": "🚚",
}


# ============================================================
# DASHBOARD STYLE
# ============================================================

def _dashboard_style():

    st.markdown(
        """
        <style>

        /* ==================================================
           MAIN DASHBOARD
           ================================================== */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }


        /* ==================================================
           PAGE TITLE
           ================================================== */

        .dashboard-title {
            font-size: 32px;
            font-weight: 800;
            color: #172033;
            margin-bottom: 2px;
            letter-spacing: -0.5px;
        }


        /* ==================================================
           ANIMATED PAGE INTRO
           ================================================== */

        .dashboard-intro {
            animation: fadeDown 0.55s ease-out;
        }

        @keyframes fadeDown {

            from {
                opacity: 0;
                transform: translateY(-10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }

        }


        /* ==================================================
           SECTION TITLES
           ================================================== */

        .section-title {
            font-size: 18px;
            font-weight: 750;
            color: #172033;
            margin-top: 26px;
            margin-bottom: 12px;
        }


        /* ==================================================
           CHART CONTAINERS
           ================================================== */

        div[data-testid="stVerticalBlockBorderWrapper"] {

            border-radius: 16px !important;

            border: 1px solid #E8ECF2 !important;

            box-shadow:
                0 4px 16px rgba(23, 32, 51, 0.045);

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease;

        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {

            transform: translateY(-2px);

            box-shadow:
                0 10px 28px rgba(23, 32, 51, 0.08);

        }


        /* ==================================================
           CHART HEADER
           ================================================== */

        .chart-heading {
            font-size: 15px;
            font-weight: 750;
            color: #172033;
            margin-bottom: 1px;
        }

        .chart-description {
            font-size: 12px;
            color: #8A93A2;
            margin-bottom: 6px;
        }


        /* ==================================================
           RECENT ACTIVITY
           ================================================== */

        .activity-row {

            padding: 11px 4px;

            border-bottom:
                1px solid #EEF1F5;

            transition:
                background 0.2s ease,
                padding-left 0.2s ease;

        }

        .activity-row:hover {

            background: #FAFBFC;

            padding-left: 8px;

        }

        .activity-text {

            font-size: 13px;

            color: #263246;

        }

        .activity-time {

            font-size: 11px;

            color: #9AA3B1;

            margin-top: 3px;

        }


        /* ==================================================
           SMALL SCREEN
           ================================================== */

        @media (max-width: 900px) {

            .dashboard-title {
                font-size: 26px;
            }

            .section-title {
                font-size: 16px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CHART
# ============================================================

def _show_chart(fig, title, description):

    with st.container(border=True):

        st.markdown(
            f"**{title}**"
        )

        st.caption(
            description
        )

        st.plotly_chart(
            fig,
            width="stretch",
            config=CHART_CONFIG,
        )


# ============================================================
# RECENT ACTIVITY
# ============================================================

def _recent_activity_panel():

    st.markdown(
        "### Recent Activity"
    )

    st.caption(
        "Latest actions performed in BloodCare"
    )

    items = get_recent_activity(8)

    with st.container(border=True):

        if not items:

            st.info(
                "No activity recorded yet."
            )

            return


        for activity in items:

            icon = ACTION_ICONS.get(
                activity.get("action"),
                "•",
            )

            user_name = activity.get(
                "user_name",
                "Unknown user",
            )

            details = activity.get(
                "details",
                "Activity recorded",
            )

            created_at = activity.get(
                "created_at"
            )


            if created_at:

                try:

                    when = created_at.strftime(
                        "%d %b %Y • %I:%M %p"
                    )

                except Exception:

                    when = str(created_at)

            else:

                when = "Time unavailable"


            st.markdown(
                f"""
                <div class="activity-row">
                    <div class="activity-text">
                        {icon} <strong>{user_name}</strong>
                        &nbsp; {details}
                    </div>
                    <div class="activity-time">
                        {when}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard():

    # Load dashboard styling
    _dashboard_style()


    # ========================================================
    # GET DATA
    # ========================================================

    k = get_kpis()


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        "## Dashboard"
    )

    st.caption(
        "Home / Dashboard"
    )


    # ========================================================
    # OVERVIEW
    # ========================================================

    st.markdown(
        "### Overview"
    )


    # ========================================================
    # KPI ROW 1
    # ========================================================

    row1 = st.columns(
        3,
        gap="medium",
    )


    with row1[0]:

        kpi_card(
            "🩸",
            k["total_units"],
            "Total Blood Units",
            "All units in system",
            "red",
            "up",
        )


    with row1[1]:

        kpi_card(
            "✅",
            k["available"],
            "Available Units",
            "Ready to issue",
            "green",
            "up",
        )


    with row1[2]:

        kpi_card(
            "⚠️",
            k["low_stock"],
            "Low Stock Groups",
            "Need refill",
            "amber",
            "warn",
        )


    # ========================================================
    # KPI ROW 2
    # ========================================================

    row2 = st.columns(
        3,
        gap="medium",
    )


    with row2[0]:

        kpi_card(
            "⏳",
            k["expiring_soon"],
            "Expiring Soon",
            "Within 7 days",
            "amber",
            "warn",
        )


    with row2[1]:

        kpi_card(
            "👥",
            k["donors"],
            "Total Donors",
            "Registered donors",
            "blue",
            "up",
        )


    with row2[2]:

        kpi_card(
            "📋",
            k["pending"],
            "Pending Requests",
            f"{k['approved']} approved",
            "red",
            "down",
        )


    # ========================================================
    # INVENTORY ANALYTICS
    # ========================================================

    st.markdown(
        "### Inventory Analytics"
    )

    st.caption(
        "Monitor blood stock and collection trends"
    )


    c1, c2 = st.columns(
        2,
        gap="medium",
    )


    # --------------------------------------------------------
    # STOCK BY GROUP
    # --------------------------------------------------------

    with c1:

        stock_data = get_stock_by_group()

        _show_chart(
            stock_chart(stock_data),
            "Blood Stock by Group",
            "Current blood units available by blood group",
        )


    # --------------------------------------------------------
    # MONTHLY COLLECTION
    # --------------------------------------------------------

    with c2:

        labels, values = get_monthly_collection()

        _show_chart(
            monthly_chart(labels, values),
            "Monthly Blood Collection",
            "Blood collection trend over recent months",
        )


    # ========================================================
    # OPERATIONS
    # ========================================================

    st.markdown(
        "### Operations Overview"
    )

    st.caption(
        "Track requests and blood expiry status"
    )


    c3, c4 = st.columns(
        2,
        gap="medium",
    )


    # --------------------------------------------------------
    # REQUEST STATUS
    # --------------------------------------------------------

    with c3:

        request_data = get_request_status_counts()

        _show_chart(
            request_chart(request_data),
            "Blood Request Status",
            "Current distribution of blood requests",
        )


    # --------------------------------------------------------
    # EXPIRY
    # --------------------------------------------------------

    with c4:

        expiry_data = get_expiry_overview()

        _show_chart(
            expiry_chart(expiry_data),
            "Blood Expiry Overview",
            "Units grouped according to expiry status",
        )


    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    _recent_activity_panel()