
from sqlalchemy import text

from chart_service import get_stock_by_group
from database import engine
from expiry_service import get_expiry_units
from request_service import get_requests


LOW_STOCK_THRESHOLD = 2


# ============================================================
# UNIT LIST HELPER
# ============================================================

def _unit_list(units, limit=5):
    codes = ", ".join(
        u["unit_code"]
        for u in units[:limit]
    )

    extra = len(units) - limit

    return (
        f"{codes} and {extra} more"
        if extra > 0
        else codes
    )


# ============================================================
# BUILD ALERTS
# ============================================================

def build_alerts():
    """
    Abhi ke database data se alerts ki list banata hai.
    Database mein kuch save nahi karta.
    """

    alerts = []

    # --------------------------------------------------------
    # 1. LOW STOCK
    # --------------------------------------------------------

    for group, count in get_stock_by_group().items():

        if count < LOW_STOCK_THRESHOLD:

            alerts.append({
                "title": f"Low stock: {group}",
                "message": (
                    f"Only {count} unit(s) of "
                    f"{group} available."
                ),
                "category": "stock",
                "severity": "warning",
            })

    # --------------------------------------------------------
    # 2. EXPIRY ALERTS
    # --------------------------------------------------------

    expiring = []
    expired = []

    for u in get_expiry_units():

        if u["bucket"] == "Expired":
            expired.append(u)

        elif u["bucket"] in (
            "Expires today",
            "Within 7 days"
        ):
            expiring.append(u)

    # Expiring soon

    if expiring:

        alerts.append({
            "title": "Blood expiring within 7 days",
            "message": (
                f"{len(expiring)} unit(s) will expire "
                f"within 7 days: "
                f"{_unit_list(expiring)}."
            ),
            "category": "expiry",
            "severity": "warning",
        })

    # Already expired

    if expired:

        alerts.append({
            "title": "Expired blood needs discarding",
            "message": (
                f"{len(expired)} unit(s) have expired: "
                f"{_unit_list(expired)}. "
                f"Please discard them."
            ),
            "category": "expiry",
            "severity": "danger",
        })

    # --------------------------------------------------------
    # 3. EMERGENCY REQUESTS
    # --------------------------------------------------------

    emergencies = [
        r
        for r in get_requests(
            urgency="Emergency"
        )
        if r["status"] in (
            "Pending",
            "Approved"
        )
    ]

    for r in emergencies[:5]:

        alerts.append({
            "title": (
                f"Emergency request: "
                f"{r['request_code']}"
            ),
            "message": (
                f"{r['units_required']} unit(s) of "
                f"{r['blood_group']} needed at "
                f"{r['hospital_name']} for "
                f"{r['patient_name']} "
                f"({r['status']})."
            ),
            "category": "request",
            "severity": "danger",
        })

    if len(emergencies) > 5:

        alerts.append({
            "title": "More emergency requests",
            "message": (
                f"{len(emergencies) - 5} more "
                f"emergency request(s) are open. "
                f"See the Requests page."
            ),
            "category": "request",
            "severity": "danger",
        })

    # --------------------------------------------------------
    # 4. PENDING REQUESTS
    # --------------------------------------------------------

    pending = len(
        get_requests(
            status="Pending"
        )
    )

    if pending:

        alerts.append({
            "title": "Pending requests",
            "message": (
                f"{pending} blood request(s) "
                f"are waiting for approval."
            ),
            "category": "request",
            "severity": "info",
        })

    return alerts


# ============================================================
# SYNC ALERTS
# ============================================================

def sync_alerts():
    """
    Naye alerts save karta hai.
    Purane resolved unread alerts remove karta hai.
    """

    current = {
        (a["title"], a["message"]): a
        for a in build_alerts()
    }

    with engine.begin() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    id,
                    title,
                    message,
                    is_read
                FROM notifications
            """)
        ).mappings().all()

        existing = {
            (r["title"], r["message"])
            for r in rows
        }

        # ----------------------------------------------------
        # REMOVE RESOLVED UNREAD ALERTS
        # ----------------------------------------------------

        removed = 0

        for r in rows:

            if (
                not r["is_read"]
                and (r["title"], r["message"]) not in current
            ):

                conn.execute(
                    text("""
                        DELETE FROM notifications
                        WHERE id = :id
                    """),
                    {
                        "id": r["id"]
                    }
                )

                removed += 1

        # ----------------------------------------------------
        # ADD NEW ALERTS
        # ----------------------------------------------------

        added = 0

        for key, alert in current.items():

            if key in existing:
                continue

            conn.execute(
                text("""
                    INSERT INTO notifications
                    (
                        title,
                        message,
                        category,
                        severity,
                        is_read,
                        created_at,
                        updated_at
                    )

                    VALUES
                    (
                        :title,
                        :message,
                        :category,
                        :severity,
                        0,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                """),
                alert,
            )

            added += 1

    return added, removed


# ============================================================
# GET NOTIFICATIONS
# ============================================================

def get_notifications(
    category="All",
    only_unread=False
):

    sql = """
        SELECT
            id,
            title,
            message,
            category,
            severity,
            is_read,
            created_at

        FROM notifications

        WHERE 1 = 1
    """

    params = {}

    # --------------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------------

    if category != "All":

        sql += """
            AND category = :category
        """

        params["category"] = category

    # --------------------------------------------------------
    # UNREAD FILTER
    # --------------------------------------------------------

    if only_unread:

        sql += """
            AND is_read = 0
        """

    # --------------------------------------------------------
    # SQLITE SEVERITY SORT
    #
    # danger  = 1
    # warning = 2
    # info    = 3
    # --------------------------------------------------------

    sql += """
        ORDER BY
            is_read ASC,

            CASE
                WHEN severity = 'danger' THEN 1
                WHEN severity = 'warning' THEN 2
                WHEN severity = 'info' THEN 3
                ELSE 4
            END,

            created_at DESC,
            id DESC
    """

    with engine.connect() as conn:

        rows = conn.execute(
            text(sql),
            params
        ).mappings().all()

    return [
        dict(r)
        for r in rows
    ]


# ============================================================
# MARK ONE AS READ
# ============================================================

def mark_read(notification_id):

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE notifications

                SET
                    is_read = 1,
                    updated_at = CURRENT_TIMESTAMP

                WHERE id = :id
            """),
            {
                "id": notification_id
            }
        )


# ============================================================
# MARK ALL AS READ
# ============================================================

def mark_all_read():

    with engine.begin() as conn:

        conn.execute(
            text("""
                UPDATE notifications

                SET
                    is_read = 1,
                    updated_at = CURRENT_TIMESTAMP

                WHERE is_read = 0
            """)
        )

