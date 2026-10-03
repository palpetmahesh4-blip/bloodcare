# Kaun si action kaunse role ko allowed hai, sab yahin likha hai.
PERMISSIONS = {
    "admin": {
        "delete_unit", "delete_donor", "discard_unit",
        "approve_request", "reject_request", "manage_users", "view_logs",
    },
    "staff": set(),
}


def can(user, action):
    """True agar is user ka role is action ki ijazat deta hai."""
    return action in PERMISSIONS.get(user["role"], set())