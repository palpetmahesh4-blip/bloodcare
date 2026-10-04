import streamlit as st

from activity_service import log_activity
from auth import authenticate
from user_service import create_user
from dashboard import render_dashboard
from distribution_page import render_distribution
from donor_page import render_donors
from expiry_page import render_expiry
from inventory_page import render_inventory
from notification_page import render_notifications
from notification_service import sync_alerts
from queries import get_unread_count
from report_page import render_reports
from request_page import render_requests
from settings_page import render_settings
from ui import load_css, topbar
from search_page import render_search_results


st.set_page_config(
    page_title="BloodCare",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded",
)


try:
    load_css()
except Exception:
    pass



st.markdown(
    """
    <style>

    .bloodcare-login-title {
        font-size: 42px;
        font-weight: 800;
        color: #B3122D;
        margin-top: 80px;
        margin-bottom: 4px;
    }

    .bloodcare-login-subtitle {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #6B7280;
        margin-bottom: 22px;
    }

    .bloodcare-description {
        color: #6B7280;
        font-size: 15px;
        line-height: 1.7;
        margin-bottom: 25px;
        max-width: 500px;
    }

    .bloodcare-feature {
        padding: 9px 0;
        color: #1B2A41;
        font-size: 14px;
    }

    .bloodcare-feature-icon {
        color: #B3122D;
        font-weight: 800;
        margin-right: 9px;
    }

    .login-title {
        font-size: 30px;
        font-weight: 800;
        color: #1B2A41;
        margin-top: 80px;
        margin-bottom: 5px;
    }

    .login-subtitle {
        font-size: 14px;
        color: #6B7280;
        margin-bottom: 25px;
    }

    .bloodcare-logo {
        width: 70px;
        height: 70px;
        border-radius: 18px;

        background: linear-gradient(
            145deg,
            #D51F3C,
            #A80F29
        );

        display: flex;
        align-items: center;
        justify-content: center;

        margin-top: 55px;
        margin-bottom: 20px;

        box-shadow:
            0 12px 28px rgba(179, 18, 45, 0.22);

        position: relative;
    }

    .bloodcare-logo::before {
        content: "";

        width: 35px;
        height: 42px;

        background: white;

        position: absolute;

        clip-path: polygon(
            50% 0%,
            92% 15%,
            92% 55%,
            75% 79%,
            50% 100%,
            25% 79%,
            8% 55%,
            8% 15%
        );
    }

    .bloodcare-logo::after {
        content: "";

        width: 15px;
        height: 22px;

        background: #B3122D;

        position: absolute;

        clip-path: polygon(
            50% 0%,
            88% 48%,
            92% 68%,
            80% 85%,
            64% 96%,
            50% 100%,
            36% 96%,
            20% 85%,
            8% 68%,
            12% 48%
        );
    }

    </style>
    """,
    unsafe_allow_html=True,
)


MENU = [
    "📊 Dashboard",
    "🩸 Inventory",
    "👥 Donors",
    "📋 Requests",
    "🚚 Distribution",
    "⏳ Expiry",
    "📑 Reports",
    "🔔 Notifications",
    "⚙️ Settings",
]



if "user" not in st.session_state:


    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "🔐 Sign In"


    left_col, right_col = st.columns(
        [1.05, 0.95],
        gap="large",
    )



    with left_col:

        st.markdown(
            '<div class="bloodcare-logo"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-login-title">BloodCare</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-login-subtitle">'
            'BLOOD BANK MANAGEMENT SYSTEM'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-description">'
            'A smarter way to manage blood inventory, '
            'donors, requests, expiry and distribution '
            'from one secure platform.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-feature">'
            '<span class="bloodcare-feature-icon">✓</span>'
            'Real-time blood inventory'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-feature">'
            '<span class="bloodcare-feature-icon">✓</span>'
            'Donor management'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-feature">'
            '<span class="bloodcare-feature-icon">✓</span>'
            'Blood request management'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-feature">'
            '<span class="bloodcare-feature-icon">✓</span>'
            'Smart expiry and low-stock alerts'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="bloodcare-feature">'
            '<span class="bloodcare-feature-icon">✓</span>'
            'Distribution tracking'
            '</div>',
            unsafe_allow_html=True,
        )


    with right_col:

        st.markdown(
            '<div class="login-title">Welcome to BloodCare</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-subtitle">'
            'Sign in to your account or create a new staff account.'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("")


        selected_auth = st.radio(
            "Authentication",
            [
                "🔐 Sign In",
                "➕ Create Account",
            ],
            index=(
                0
                if st.session_state["auth_page"] == "🔐 Sign In"
                else 1
            ),
            horizontal=True,
            label_visibility="collapsed",
        )


        st.session_state["auth_page"] = selected_auth

        st.write("")


        if selected_auth == "🔐 Sign In":


            if st.session_state.get("signup_success", False):

                st.success(
                    "✅ Account created successfully! "
                    "You can now sign in with your new account."
                )

                st.session_state["signup_success"] = False


            st.subheader(
                "Welcome back"
            )

            st.caption(
                "Sign in to continue to BloodCare."
            )


            email = st.text_input(
                "Email",
                placeholder="Enter your email",
                key="login_email",
            )


            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )


            st.write("")


            if st.button(
                "Sign In",
                type="primary",
                width="stretch",
                key="signin_button",
            ):

                if not email.strip():

                    st.error(
                        "Please enter your email."
                    )

                elif not password:

                    st.error(
                        "Please enter your password."
                    )

                else:

                    try:

                        logged_user = authenticate(
                            email.strip(),
                            password,
                        )


                        if logged_user:

                            st.session_state["user"] = logged_user

                            st.rerun()


                        else:

                            st.error(
                                "Invalid email or password."
                            )


                    except Exception as e:

                        st.error(
                            f"Login error: {e}"
                        )



        else:

            st.subheader(
                "Create your account"
            )

            st.caption(
                "Register a new BloodCare staff account."
            )


            with st.form(
                "signup_form",
                clear_on_submit=False,
            ):

                full_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name",
                )


                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                )


                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Minimum 8 characters",
                )


                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                )


                st.write("")


                st.info(
                    "New accounts are registered as Staff. "
                    "Admin access is managed separately."
                )


                st.write("")


                submitted = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    width="stretch",
                )



            if submitted:

                if not full_name.strip():

                    st.error(
                        "Please enter your full name."
                    )

                elif not email.strip():

                    st.error(
                        "Please enter your email."
                    )

                elif not password:

                    st.error(
                        "Please enter a password."
                    )

                elif len(password) < 8:

                    st.error(
                        "Password must be at least 8 characters."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    try:

                     

                        create_user(
                            full_name,
                            email,
                            password,
                            "staff",
                        )



                        st.session_state["auth_page"] = (
                            "🔐 Sign In"
                        )


                        st.session_state["signup_success"] = True


        

                        st.rerun()


                    except ValueError as e:

                        st.error(
                            str(e)
                        )


                    except Exception as e:

                        st.error(
                            f"Account creation error: {e}"
                        )


        st.write("")


        st.caption(
            "🔒 Protected healthcare management system"
        )

        st.caption(
            "BloodCare"
        )



    st.stop()



user = st.session_state["user"]


user_name = str(
    user.get("name", "User")
)


user_role = str(
    user.get("role", "Staff")
)



with st.sidebar:

    st.markdown(
        "## BloodCare"
    )

    st.caption(
        "BLOOD BANK MANAGEMENT"
    )

    st.divider()


    st.caption(
        "MAIN MENU"
    )


    page = st.radio(
        "Menu",
        MENU,
        label_visibility="collapsed",
    )


    st.divider()


    st.write(
        f"**{user_name}**"
    )

    st.caption(
        user_role
    )

    st.write("")



    if st.button(
        "↪ Sign out",
        width="stretch",
    ):

        try:

            log_activity(
                user["id"],
                "LOGOUT",
                f"{user_name} logged out",
            )

        except Exception:

            pass


        del st.session_state["user"]

        st.rerun()



if st.session_state.get("last_page") != page:

    st.session_state["last_page"] = page

    st.session_state["global_search"] = ""


try:

    sync_alerts()

except Exception:

    pass


try:

    unread_count = get_unread_count()

except Exception:

    unread_count = 0




try:

    topbar(
        user_name,
        user_role,
        unread_count,
    )

except Exception:

    pass



query = (
    st.session_state.get("global_search") or ""
).strip()


if len(query) >= 2:

    render_search_results(query)


elif page.endswith("Dashboard"):

    render_dashboard()


elif page.endswith("Inventory"):

    render_inventory()


elif page.endswith("Donors"):

    render_donors()


elif page.endswith("Requests"):

    render_requests()


elif page.endswith("Distribution"):

    render_distribution()


elif page.endswith("Expiry"):

    render_expiry()


elif page.endswith("Reports"):

    render_reports()


elif page.endswith("Notifications"):

    render_notifications()


elif page.endswith("Settings"):

    render_settings()


else:

    st.title(
        page[2:]
    )

    st.info(
        "This page will be available in the next phase."
    )