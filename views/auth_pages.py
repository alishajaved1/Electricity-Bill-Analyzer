import streamlit as st

from components.logos import auth_picture
from components.ui import logo
from utils import auth
from utils.state import navigate
from utils.validation import valid_email


def _side(title, text, bullets, pic=""):
    items = "".join(f"<li>✅ {b}</li>" for b in bullets)
    st.markdown(f'<div class="auth-side fade">{logo()}<h2 style="margin-top:1.6rem">{title}</h2><p>{text}</p><ul style="padding:0">{items}</ul>{pic}</div>',
                unsafe_allow_html=True)


def login_page():
    left, right = st.columns([1, 1.5], gap="large")
    with left:
        _side("Welcome Back!", "Login to analyze your electricity bills.", ["Track your usage", "Get cost analysis", "Receive smart suggestions"], auth_picture("auth_login.jpg"))
    with right:
        st.markdown("## Login")
        st.info("🧪 Demo login: accounts exist only for this session. Sign up first, then log in. No real account is created.")
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="Enter your email", value=st.session_state.get("remembered_email", ""))
            pw = st.text_input("Password", type="password", placeholder="Enter your password")
            c1, _ = st.columns(2)
            remember = c1.checkbox("Remember me")
            ok = st.form_submit_button("Login", type="primary", width="stretch")
        if ok:
            good, msg = auth.login(email, pw)
            if good:
                st.session_state.remembered_email = email.strip() if remember else ""
                navigate("Dashboard")
                st.rerun()
            else:
                st.error(msg)
        with st.expander("Forgot password?"):
            with st.form("forgot_form"):
                fe = st.text_input("Your email", key="forgot_email")
                if st.form_submit_button("Reset password"):
                    if not valid_email(fe):
                        st.error("Please enter a valid email address.")
                    else:
                        st.info("Demo only: no email is sent and no password is changed. Create a new demo account via Sign Up instead.")
        st.write("Don't have an account?")
        st.button("Sign Up", key="to_signup", on_click=navigate, args=("signup",))
        st.button("← Back to home", key="back_home_l", on_click=navigate, args=("landing",))


def signup_page():
    left, right = st.columns([1, 1.5], gap="large")
    with left:
        _side("Create Your Account", "Join and start analyzing your electricity today.", ["Track your usage", "Get detailed insights", "Export your history"], auth_picture("auth_signup.jpg"))
    with right:
        st.markdown("## Sign Up")
        st.info("🧪 Demo sign-up: your account is kept in memory for this session only and is lost on refresh. Passwords are hashed, never stored in plaintext.")
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email Address", placeholder="Enter your email")
            pw = st.text_input("Password", type="password", placeholder="Create a password (min. 8 characters)")
            pw2 = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            ok = st.form_submit_button("Sign Up", type="primary", width="stretch")
        if ok:
            good, errs = auth.register(name, email, pw, pw2)
            if good:
                auth.login(email, pw)
                navigate("Dashboard")
                st.rerun()
            else:
                for e in errs:
                    st.error(e)
        st.write("Already have an account?")
        st.button("Login", key="to_login", on_click=navigate, args=("login",))
        st.button("← Back to home", key="back_home_s", on_click=navigate, args=("landing",))
