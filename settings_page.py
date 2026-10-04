import pandas as pd
import streamlit as st

from activity_service import log_activity, get_activity_logs, get_action_types
from user_service import change_password, list_users, create_user, set_user_active


def _profile_tab(user):
    initials = "".join(w[0] for w in user["name"].replace("Dr. ", "").split()[:2]).upper()

    with st.container(border=True):
        c1, c2 = st.columns([1, 5], vertical_alignment="center")
        with c1:
            st.markdown(
                f'<div class="topbar-avatar" style="width:64px;height:64px;font-size:1.4rem;">'
                f"{initials}</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(f"### {user['name']}")
            st.caption(user["role"].title())

        st.markdown(f"**Email:** {user['email']}")
        st.markdown(f"**Role:** {user['role'].title()}")
        if user["role"] == "admin":
            st.caption("Admins can manage users and view all activity logs.")
        else:
            st.caption("Staff can manage inventory, donors, requests and distribution.")


def _password_tab(user):
    with st.container(border=True):
        st.markdown("#### Change password")
        st.caption("Use at least 8 characters.")

        with st.form("change_password_form", clear_on_submit=True):
            current = st.text_input("Current password", type="password")
            new = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Update password")

        if submitted:
            if not current or not new or not confirm:
                st.error("Please fill in all three fields.")
            elif new != confirm:
                st.error("New password and confirmation do not match.")
            else:
                try:
                    change_password(user["id"], current, new)
                    log_activity(user["id"], "CHANGE_PASSWORD", f"{user['name']} changed their password")
                    st.success("Password updated successfully.")
                except ValueError as e:
                    st.error(str(e))


@st.dialog("Add User")
def add_user_dialog():
    with st.form("add_user_form"):
        full_name = st.text_input("Full name", placeholder="e.g. Anita Kulkarni")
        email = st.text_input("Email", placeholder="anita@bloodbank.in")
        c1, c2 = st.columns(2)
        with c1:
            role = st.selectbox("Role", ["staff", "admin"])
        with c2:
            password = st.text_input("Temporary password", type="password")
        submitted = st.form_submit_button("Create user")

    if submitted:
        try:
            created = create_user(full_name, email, password, role)
            log_activity(
                st.session_state["user"]["id"], "CREATE_USER", f"Created {role} user {created}"
            )
            st.session_state["flash"] = f"User {created} created"
            st.rerun()
        except ValueError as e:
            st.error(str(e))


def _users_tab(current_user):
    if st.button("➕ Add user"):
        add_user_dialog()

    users = list_users()
    df = pd.DataFrame(users)
    df["Status"] = df["is_active"].map(
        {1: "Active", 0: "Inactive", True: "Active", False: "Inactive"}
    )
    df["role"] = df["role"].str.title()
    df = df.rename(columns={
        "full_name": "Name",
        "email": "Email",
        "role": "Role",
        "created_at": "Created",
    })[["Name", "Email", "Role", "Status", "Created"]]

    st.caption(f"{len(df)} users")

    event = st.dataframe(
        df,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="users_table",
    )

    selected = event.selection.rows
    if selected:
        target = users[selected[0]]
        is_active = bool(target["is_active"])
        st.markdown(
            f"Selected user: **{target['full_name']}** "
            f"({'Active' if is_active else 'Inactive'})"
        )

        if target["id"] == current_user["id"]:
            st.caption("This is your own account, so it cannot be deactivated.")
        elif is_active:
            if st.button("⛔ Deactivate user"):
                try:
                    set_user_active(target["id"], False, current_user["id"])
                    log_activity(
                        current_user["id"], "DEACTIVATE_USER", f"Deactivated user {target['email']}"
                    )
                    st.session_state["flash"] = f"User {target['email']} deactivated"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        else:
            if st.button("✅ Activate user"):
                set_user_active(target["id"], True, current_user["id"])
                log_activity(
                    current_user["id"], "ACTIVATE_USER", f"Activated user {target['email']}"
                )
                st.session_state["flash"] = f"User {target['email']} activated"
                st.rerun()


def _logs_tab():
    f1, f2 = st.columns([3, 1.8])
    with f1:
        search = st.text_input(
            "Search",
            placeholder="Search by user or details",
            key="log_search",
        )
    with f2:
        action = st.selectbox("Action", ["All"] + get_action_types(), key="log_action")

    logs = get_activity_logs(search, action)

    if not logs:
        st.info("No activity logs found for these filters.")
        return

    df = pd.DataFrame(logs).rename(columns={
        "created_at": "When",
        "user_name": "User",
        "action": "Action",
        "details": "Details",
    })[["When", "User", "Action", "Details"]]

    st.caption(f"{len(df)} log entries (latest 200 shown at most)")
    st.dataframe(df, width="stretch", hide_index=True)


def render_settings():
    user = st.session_state["user"]

    st.markdown("## Settings")
    st.caption("Home / Settings")

    if "flash" in st.session_state:
        st.toast(st.session_state.pop("flash"), icon="✅")

    tab_names = ["👤 Profile", "🔑 Password"]
    if user["role"] == "admin":
        tab_names += ["👥 Users", "📜 Activity logs"]

    tabs = st.tabs(tab_names)

    with tabs[0]:
        _profile_tab(user)

    with tabs[1]:
        _password_tab(user)

    if user["role"] == "admin":
        with tabs[2]:
            _users_tab(user)
        with tabs[3]:
            _logs_tab()