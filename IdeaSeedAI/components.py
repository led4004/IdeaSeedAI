import streamlit as st
from database import db


# ============================================================
# 공통 카드 시작
# ============================================================

def card_start():

    st.markdown(
        """
        <div class="idea-card">
        """,
        unsafe_allow_html=True
    )


def card_end():

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# Header
# ============================================================

def render_header():

    profile = db.get_profile()

    level = profile["level"]
    exp = profile["exp"]

    need = level * 100

    percent = exp / need

    if percent > 1:
        percent = 1

    st.markdown(
        f"""
<div class="header-card">

<div class="title">

🌱 아이디어 새싹 AI

</div>

<div class="subtitle">

오늘도 새로운 아이디어를 키워볼까요?

</div>

<div class="level">

LV. {level}

</div>

<div class="xp">

{exp} / {need} XP

</div>

</div>
""",
        unsafe_allow_html=True
    )

    st.progress(percent)


# ============================================================
# Profile Card
# ============================================================

def profile_card():

    profile = db.get_profile()

    st.markdown("### 👦 연구원 정보")

    card_start()

    c1, c2 = st.columns(2)

    with c1:

        st.metric(

            "🏆 Level",

            profile["level"]

        )

    with c2:

        st.metric(

            "⭐ EXP",

            profile["exp"]

        )

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "🌳 연구",

            profile["total_topics"]

        )

    with c2:

        st.metric(

            "📕 실패",

            profile["total_failures"]

        )

    with c3:

        st.metric(

            "🤖 AI",

            profile["total_chats"]

        )

    card_end()


# ============================================================
# Dashboard
# ============================================================

def dashboard():

    data = db.dashboard()

    st.markdown("## 📊 연구 현황")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "🌳 연구주제",

            data["topics"]

        )

        st.metric(

            "🍎 완성",

            data["finished"]

        )

    with c2:

        st.metric(

            "📕 실패노트",

            data["failures"]

        )

        st.metric(

            "🤖 AI대화",

            data["chats"]

        )

    with c3:

        st.metric(

            "⭐ 평균점수",

            data["average"]

        )

        st.metric(

            "🏆 LEVEL",

            data["profile"]["level"]

        )

# ============================================================
# Mission Panel
# ============================================================

def mission_panel():

    st.markdown("## 🎯 오늘의 미션")

    missions = db.get_missions()

    if len(missions) == 0:

        st.info("등록된 미션이 없습니다.")

        return

    for mission in missions:

        completed = mission["completed"] == 1

        col1, col2 = st.columns([6,1])

        with col1:

            if completed:

                st.success(
                    f"✅ {mission['title']}"
                )

            else:

                st.info(
                    f"🎯 {mission['title']}"
                )

        with col2:

            if completed:

                st.write("🏆")

            else:

                if st.button(

                    "완료",

                    key=f"mission_{mission['id']}"

                ):

                    db.complete_mission(

                        mission["id"]

                    )

                    st.rerun()


# ============================================================
# Badge Panel
# ============================================================

def badge_panel():

    st.markdown("## 🏅 배지")

    badges = db.get_badges()

    cols = st.columns(3)

    for i, badge in enumerate(badges):

        with cols[i % 3]:

            if badge["unlocked"]:

                st.success(
                    f"""
{badge['icon']}

**{badge['name']}**

{badge['description']}
"""
                )

            else:

                st.warning(
                    """
🔒

잠김
"""
                )


# ============================================================
# Statistic Card
# ============================================================

def statistic_card():

    st.markdown("## 📈 연구 통계")

    profile = db.get_profile()

    st.progress(

        profile["exp"] /

        (profile["level"] * 100)

    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "🌳 연구",

            profile["total_topics"]

        )

    with c2:

        st.metric(

            "📕 실패",

            profile["total_failures"]

        )

    with c3:

        st.metric(

            "🤖 AI",

            profile["total_chats"]

        )


# ============================================================
# Empty Card
# ============================================================

def empty_card(

    title,

    message,

    icon="🌱"

):

    st.markdown(

        f"""
<div class="empty-card">

<h2>{icon}</h2>

<h3>{title}</h3>

<p>{message}</p>

</div>
""",

        unsafe_allow_html=True

    )


# ============================================================
# Loading Card
# ============================================================

def loading_card(text="불러오는 중..."):

    with st.spinner(text):

        pass


# ============================================================
# AI Thinking
# ============================================================

def ai_thinking():

    st.info(

        "🤖 AI 연구조교가 생각하고 있습니다..."

    )


# ============================================================
# Footer
# ============================================================

def footer():

    st.divider()

    st.caption(

        "🌱 Idea Seed AI 2026"

    )


# ============================================================
# Sidebar
# ============================================================

def render_sidebar():

    profile = db.get_profile()

    with st.sidebar:

        st.image(

            "https://cdn-icons-png.flaticon.com/512/2909/2909768.png",

            width=90

        )

        st.title(

            profile["nickname"]

        )

        st.write("")

        st.metric(

            "🏆 Level",

            profile["level"]

        )

        st.metric(

            "⭐ EXP",

            profile["exp"]

        )

        st.divider()

        st.write("### 🌳 연구")

        st.write(

            f"총 연구 : {profile['total_topics']}"

        )

        st.write(

            f"실패노트 : {profile['total_failures']}"

        )

        st.write(

            f"AI 대화 : {profile['total_chats']}"

        )

        st.divider()

        st.success(

            "오늘도 새로운 아이디어를 키워보세요! 🌱"

        )


