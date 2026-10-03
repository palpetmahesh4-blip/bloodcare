import plotly.graph_objects as go


# ============================================================
# BLOODCARE THEME
# ============================================================

NAVY = "#1B2A41"
RED = "#B3122D"

GREEN = "#16A34A"
AMBER = "#D97706"
BLUE = "#2563EB"
DARK_RED = "#DC2626"

LOW_STOCK_THRESHOLD = 2


# ============================================================
# BASE LAYOUT
# ============================================================

def _base_layout(
    fig,
    title,
    height=330,
):

    fig.update_layout(

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title=dict(
            text=title,
            font=dict(
                size=17,
                color=NAVY,
                family="Inter, Arial, sans-serif",
            ),
            x=0.02,
            xanchor="left",
        ),

        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        height=height,

        # ----------------------------------------------------
        # SPACING
        # ----------------------------------------------------

        margin=dict(
            l=45,
            r=20,
            t=60,
            b=45,
        ),

        # ----------------------------------------------------
        # BACKGROUND
        # ----------------------------------------------------

        paper_bgcolor="white",
        plot_bgcolor="white",

        # ----------------------------------------------------
        # FONT
        # ----------------------------------------------------

        font=dict(
            family="Inter, Arial, sans-serif",
            color=NAVY,
        ),

        # ----------------------------------------------------
        # INTERACTION
        # ----------------------------------------------------

        hoverlabel=dict(
            bgcolor=NAVY,
            font=dict(
                color="white",
                size=12,
            ),
            bordercolor=NAVY,
        ),

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        transition=dict(
            duration=500,
            easing="cubic-in-out",
        ),

        # ----------------------------------------------------
        # LEGEND
        # ----------------------------------------------------

        showlegend=False,

    )


    # ========================================================
    # Y AXIS
    # ========================================================

    fig.update_yaxes(

        gridcolor="#E9EDF2",

        gridwidth=1,

        zeroline=False,

        showline=False,

        tickfont=dict(
            size=11,
            color="#7A8494",
        ),

        title_font=dict(
            size=11,
            color="#6B7280",
        ),

    )


    # ========================================================
    # X AXIS
    # ========================================================

    fig.update_xaxes(

        showgrid=False,

        showline=False,

        tickfont=dict(
            size=11,
            color="#7A8494",
        ),

    )


    return fig


# ============================================================
# BLOOD STOCK BY GROUP
# ============================================================

def stock_chart(stock):

    groups = list(stock.keys())

    counts = list(stock.values())


    # --------------------------------------------------------
    # LOW STOCK HIGHLIGHT
    # --------------------------------------------------------

    colors = [
        RED if count < LOW_STOCK_THRESHOLD else NAVY
        for count in counts
    ]


    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            x=groups,

            y=counts,

            marker=dict(
                color=colors,

                line=dict(
                    width=0,
                ),
            ),

            text=counts,

            textposition="outside",

            textfont=dict(
                size=12,
                color=NAVY,
            ),

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Available: %{y} units"
                "<extra></extra>"
            ),

            cliponaxis=False,

        )

    )


    # --------------------------------------------------------
    # AXIS
    # --------------------------------------------------------

    fig.update_yaxes(
        title_text="Available units",
        rangemode="tozero",
    )


    # --------------------------------------------------------
    # EXTRA SPACE ABOVE BARS
    # --------------------------------------------------------

    maximum = max(counts) if counts else 1

    fig.update_yaxes(
        range=[
            0,
            maximum + max(2, maximum * 0.18),
        ]
    )


    return _base_layout(
        fig,
        "Blood Stock by Group",
        340,
    )


# ============================================================
# MONTHLY BLOOD COLLECTION
# ============================================================

def monthly_chart(labels, values):

    fig = go.Figure()


    fig.add_trace(

        go.Scatter(

            x=labels,

            y=values,

            mode="lines+markers",

            line=dict(
                color=RED,
                width=3,
                shape="spline",
            ),

            marker=dict(

                size=9,

                color=RED,

                line=dict(
                    color="white",
                    width=2,
                ),

            ),

            fill="tozeroy",

            fillcolor="rgba(179, 18, 45, 0.07)",

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "Collected: %{y} units"
                "<extra></extra>"
            ),

        )

    )


    # --------------------------------------------------------
    # Y AXIS
    # --------------------------------------------------------

    fig.update_yaxes(
        title_text="Units collected",
        rangemode="tozero",
    )


    # --------------------------------------------------------
    # HOVER MODE
    # --------------------------------------------------------

    fig.update_layout(
        hovermode="x unified",
    )


    return _base_layout(
        fig,
        "Monthly Blood Collection",
        340,
    )


# ============================================================
# BLOOD REQUEST STATUS
# ============================================================

def request_chart(counts):

    colors = {

        "Pending": AMBER,

        "Approved": BLUE,

        "Fulfilled": GREEN,

        "Rejected": DARK_RED,

    }


    labels = list(
        counts.keys()
    )

    values = list(
        counts.values()
    )


    total = sum(values)


    # --------------------------------------------------------
    # DONUT
    # --------------------------------------------------------

    fig = go.Figure(

        go.Pie(

            labels=labels,

            values=values,

            hole=0.64,

            marker=dict(

                colors=[
                    colors.get(
                        label,
                        NAVY,
                    )
                    for label in labels
                ],

                line=dict(
                    color="white",
                    width=3,
                ),

            ),

            textinfo="percent",

            textfont=dict(
                size=12,
                color=NAVY,
            ),

            hovertemplate=(
                "<b>%{label}</b>"
                "<br>"
                "%{value} requests"
                "<br>"
                "%{percent}"
                "<extra></extra>"
            ),

            sort=False,

        )

    )


    # --------------------------------------------------------
    # CENTER TOTAL
    # --------------------------------------------------------

    fig.add_annotation(

        text=(
            f"<b>{total}</b>"
            "<br>"
            "<span style='font-size:11px'>"
            "Total Requests"
            "</span>"
        ),

        x=0.5,

        y=0.5,

        showarrow=False,

        font=dict(
            size=20,
            color=NAVY,
        ),

    )


    fig = _base_layout(
        fig,
        "Blood Requests by Status",
        340,
    )


    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    fig.update_layout(

        showlegend=True,

        legend=dict(

            orientation="h",

            y=-0.08,

            x=0.5,

            xanchor="center",

            font=dict(
                size=11,
                color="#5F6B7A",
            ),

        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=65,
        ),

    )


    return fig


# ============================================================
# EXPIRY OVERVIEW
# ============================================================

def expiry_chart(counts):

    colors = {

        "Expired": DARK_RED,

        "Expires today": DARK_RED,

        "Within 7 days": AMBER,

        "Within 30 days": BLUE,

        "Safe": GREEN,

    }


    labels = list(
        counts.keys()
    )

    values = list(
        counts.values()
    )


    fig = go.Figure()


    fig.add_trace(

        go.Bar(

            x=labels,

            y=values,

            marker=dict(

                color=[
                    colors.get(
                        label,
                        NAVY,
                    )
                    for label in labels
                ],

                line=dict(
                    width=0,
                ),

            ),

            text=values,

            textposition="outside",

            textfont=dict(
                size=12,
                color=NAVY,
            ),

            hovertemplate=(
                "<b>%{x}</b>"
                "<br>"
                "%{y} units"
                "<extra></extra>"
            ),

            cliponaxis=False,

        )

    )


    # --------------------------------------------------------
    # Y AXIS
    # --------------------------------------------------------

    fig.update_yaxes(
        title_text="Units in stock",
        rangemode="tozero",
    )


    maximum = max(values) if values else 1


    fig.update_yaxes(
        range=[
            0,
            maximum + max(2, maximum * 0.18),
        ]
    )


    return _base_layout(
        fig,
        "Blood Expiry Overview",
        340,
    )