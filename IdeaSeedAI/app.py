import streamlit as st

from styles import load_css

from components import (
    render_header,
    render_sidebar,
    home_menu,
    dashboard,
    badge_panel,
    mission_panel,
    today_card,
    footer,
    market_page
)

from auth import initialize_auth, is_logged_in, render_login

from tabs import (
    tree,
    mentor,
    failure,
    research,
    workflow
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="🌱 아이디어 새싹 AI",

    page_icon="🌱",

    layout="wide",

    initial_sidebar_state="expanded"

)

load_css()

initialize_auth()

if not is_logged_in():
    render_login()
    st.stop()


# ==========================================================
# SESSION
# ==========================================================

if "page" not in st.session_state:

    st.session_state.page = "home"


# ==========================================================
# SIDEBAR
# ==========================================================

render_sidebar()


# ==========================================================
# HEADER
# ==========================================================

render_header()


# ==========================================================
# HOME
# ==========================================================

if st.session_state.page == "home":

    today_card()

    st.write("")

    home_menu()

    st.divider()

    dashboard()

    st.divider()

    left, right = st.columns(2)

    with left:

        badge_panel()

    with right:

        mission_panel()

    footer()


# ==========================================================
# TREE PAGE
# ==========================================================

elif st.session_state.page == "tree":

    if st.button(
        "⬅ 홈으로",
        use_container_width=False
    ):
        st.session_state.page = "home"
        st.rerun()

    tree.render()

    footer()


# ==========================================================
# MENTOR PAGE
# ==========================================================

elif st.session_state.page == "mentor":

    if st.button(
        "⬅ 홈으로",
        use_container_width=False
    ):
        st.session_state.page = "home"
        st.rerun()

    mentor.render()

    footer()


# ==========================================================
# FAILURE PAGE
# ==========================================================

elif st.session_state.page == "failure":

    if st.button(
        "⬅ 홈으로",
        use_container_width=False
    ):
        st.session_state.page = "home"
        st.rerun()

    failure.render()

    footer()


# ==========================================================
# RESEARCH NOTE PAGE
# ==========================================================

elif st.session_state.page == "research":

    if st.button("⬅ 홈으로", use_container_width=False):
        st.session_state.page = "home"
        st.rerun()

    research.render()
    footer()


# ==========================================================
# FRUIT MARKET PAGE
# ==========================================================

elif st.session_state.page == "market":

    if st.button("⬅ 홈으로", use_container_width=False):
        st.session_state.page = "home"
        st.rerun()

    market_page()
    footer()


# ==========================================================
# IDEA WORKFLOW PAGES
# ==========================================================

elif st.session_state.page in ("seeds", "timeline", "evaluation", "portfolio"):

    if st.button("⬅ 홈으로", use_container_width=False):
        st.session_state.page = "home"
        st.rerun()

    workflow.render(st.session_state.page)
    footer()


# ==========================================================
# UNKNOWN PAGE
# ==========================================================

else:

    st.session_state.page = "home"

    st.rerun()
