from sqlalchemy import text
from database import engine


def log_activity(user_id, action, details=""):
    """Ek activity record likhta hai. Fail ho to app ko nahi rokta."""
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO activity_logs (user_id, action, details, created_at, updated_at)
                    VALUES (:user_id, :action, :details, NOW(), NOW())
                """),
                {"user_id": user_id, "action": action, "details": details},
            )
    except Exception:
        pass


def get_recent_activity(limit=8):
    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT a.id, a.action, a.details, a.created_at,
                       COALESCE(u.full_name, 'System') AS user_name
                FROM activity_logs a
                LEFT JOIN users u ON u.id = a.user_id
                ORDER BY a.created_at DESC, a.id DESC
                LIMIT :limit
            """),
            {"limit": limit},
        ).mappings().all()
    return [dict(r) for r in rows]

    

def get_activity_logs(search="", action="All", limit=200):
    sql = """
        SELECT a.id, a.action, a.details, a.created_at,
               COALESCE(u.full_name, 'System') AS user_name
        FROM activity_logs a
        LEFT JOIN users u ON u.id = a.user_id
        WHERE 1 = 1
    """
    params = {"limit": limit}

    if search:
        sql += " AND (a.details LIKE :search OR u.full_name LIKE :search)"
        params["search"] = f"%{search}%"

    if action != "All":
        sql += " AND a.action = :action"
        params["action"] = action

    sql += " ORDER BY a.created_at DESC, a.id DESC LIMIT :limit"

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


def get_action_types():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT action FROM activity_logs ORDER BY action")
        ).all()
    return [r[0] for r in rows]