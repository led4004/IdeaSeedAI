import streamlit as st
from styles import load_css


from components import (
    render_header,
    render_sidebar,
    dashboard,
    badge_panel,
    mission_panel,
    footer
)

from tabs import tree
from tabs import mentor
from tabs import failure


# =====================================
# Page Config
# =====================================

st.set_page_config(
    page_title="🌱 아이디어 새싹 AI",
    page_icon="🌱",
    layout="wide"
)

load_css()
# =====================================
# Session
# =====================================

if "page" not in st.session_state:
    st.session_state.page = "home"


# =====================================
# Sidebar
# =====================================

render_sidebar()


# =====================================
# Header
# =====================================

render_header()


# =====================================
# Home
# =====================================

if st.session_state.page == "home":

    st.write("")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "🌳 아이디어 성장나무",
            use_container_width=True
        ):

            st.session_state.page = "tree"
            st.rerun()

    with c2:

        if st.button(
            "🤖 AI 연구조교",
            use_container_width=True
        ):

            st.session_state.page = "mentor"
            st.rerun()

    c3, c4 = st.columns(2)

    with c3:

        if st.button(
            "📕 실패노트",
            use_container_width=True
        ):

            st.session_state.page = "failure"
            st.rerun()

    with c4:

        if st.button(
            "🏠 홈",
            use_container_width=True
        ):

            st.session_state.page = "home"
            st.rerun()

    st.divider()

    dashboard()

    st.divider()

    left, right = st.columns(2)

    with left:
        badge_panel()

    with right:
        mission_panel()

    footer()


# =====================================
# Tree
# =====================================

elif st.session_state.page == "tree":

    if st.button("⬅ 홈으로"):

        st.session_state.page = "home"

        st.rerun()

    tree.render()


# =====================================
# Mentor
# =====================================

elif st.session_state.page == "mentor":

    if st.button("⬅ 홈으로"):

        st.session_state.page = "home"

        st.rerun()

    mentor.render()


# =====================================
# Failure
# =====================================

elif st.session_state.page == "failure":

    if st.button("⬅ 홈으로"):

        st.session_state.page = "home"

        st.rerun()

    failure.render()