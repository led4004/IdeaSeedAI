import streamlit as st

from database import db
from components import (
    section,
    empty_card,
    success_card
)


# ==========================================================
# HEADER
# ==========================================================

def failure_header():

    st.markdown("""

<div class="header-card">

<h1>

📕 실패노트

</h1>

<p>

실패는 최고의 연구 데이터입니다.

</p>

</div>

""", unsafe_allow_html=True)


# ==========================================================
# NEW FAILURE
# ==========================================================

def add_failure():

    # sqlite3.Row 객체를 Streamlit 위젯 옵션으로 직접 넘기면
    # pickle/deepcopy 오류가 발생하므로 일반 dict로 변환합니다.
    topics = [dict(row) for row in db.get_topics()]

    if len(topics) == 0:

        empty_card(

            "연구주제가 없습니다.",

            "먼저 성장나무에서 아이디어를 심어보세요.",

            "🌱"

        )

        return False

    section("새 실패노트", "✍")

    topic_map = {
        int(topic["id"]): topic
        for topic in topics
    }

    selected_topic_id = st.selectbox(

        "연구주제",

        options=list(topic_map.keys()),

        label_visibility="collapsed",

        format_func=lambda topic_id: (
            f"{topic_map[topic_id]['fruit']} "
            f"{topic_map[topic_id]['name']}"
        ),

        key="failure_topic_select"

    )

    topic = topic_map[selected_topic_id]

    title = st.text_input(

        "실패 제목",

        placeholder="예) 바퀴가 너무 무거웠다"

    )

    reason = st.text_area(

        "왜 실패했나요?",

        placeholder="실패 원인을 적어보세요."

    )

    solution = st.text_area(

        "어떻게 해결할까요?",

        placeholder="다음에는 어떻게 고칠까요?"

    )

    learned = st.text_area(

        "이번 실패로 배운 점",

        placeholder="이번 실패에서 얻은 교훈"

    )

    if st.button(

        "💾 실패노트 저장",

        use_container_width=True

    ):

        if title.strip() == "":

            st.warning("제목을 입력하세요.")

        else:

            db.add_failure(

                topic["id"],

                title,

                reason,

                solution,

                learned

            )

            success_card(

                "실패노트를 저장했어요! 🌱"

            )

            st.rerun()

    return True


# ==========================================================
# RENDER
# ==========================================================

def render():

    failure_header()

    ok = add_failure()

    if not ok:

        return

    st.divider()

    section("저장된 실패노트", "📚")

    failures = db.get_failures()

    if len(failures) == 0:
        empty_card(
            "아직 실패노트가 없어요.",
            "실패한 기록도 멋진 연구의 일부예요.",
            "📕"
        )

        return

    for failure in failures:

        st.markdown(
            f"""
    <div class="failure-card">

    <div style="
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:14px;
    ">

    <div>

    <div style="
    font-size:14px;
    font-weight:700;
    color:#6B7280;
    margin-bottom:6px;
    ">

    {failure['fruit']} {failure['topic_name']}

    </div>

    <div style="
    font-size:22px;
    font-weight:800;
    color:#24324A;
    ">

    {failure['title']}

    </div>

    </div>

    <div style="
    font-size:34px;
    ">

    📕
    </div>

    </div>

    <div style="
    margin-top:18px;
    padding:14px;
    background:#FFF7F0;
    border-radius:16px;
    ">

    <div style="
    font-weight:800;
    margin-bottom:6px;
    ">

    😥 실패 원인

    </div>

    <div>

    {failure['reason'] if failure['reason'] else '기록된 내용이 없습니다.'}

    </div>

    </div>

    <div style="
    margin-top:12px;
    padding:14px;
    background:#F3F8FF;
    border-radius:16px;
    ">

    <div style="
    font-weight:800;
    margin-bottom:6px;
    ">

    🔧 해결 방법

    </div>

    <div>

    {failure['solution'] if failure['solution'] else '기록된 내용이 없습니다.'}

    </div>

    </div>

    <div style="
    margin-top:12px;
    padding:14px;
    background:#F1FBEF;
    border-radius:16px;
    ">

    <div style="
    font-weight:800;
    margin-bottom:6px;
    ">

    🌱 배운 점

    </div>

    <div>

    {failure['learned'] if failure['learned'] else '기록된 내용이 없습니다.'}

    </div>

    </div>

    </div>
    """,
            unsafe_allow_html=True
        )

        delete_key = f"delete_failure_{failure['id']}"
        confirm_key = f"confirm_failure_{failure['id']}"

        if st.button(
                "🗑 실패노트 삭제",
                key=delete_key,
                use_container_width=True
        ):
            st.session_state[confirm_key] = True
            st.rerun()

        if st.session_state.get(confirm_key, False):

            st.warning(
                f"'{failure['title']}' 실패노트를 정말 삭제할까요?"
            )

            yes_col, no_col = st.columns(2)

            with yes_col:

                if st.button(
                        "네, 삭제",
                        key=f"yes_{failure['id']}",
                        use_container_width=True
                ):
                    db.delete_failure(
                        failure["id"]
                    )

                    st.session_state.pop(
                        confirm_key,
                        None
                    )

                    st.rerun()

            with no_col:

                if st.button(
                        "취소",
                        key=f"no_{failure['id']}",
                        use_container_width=True
                ):
                    st.session_state.pop(
                        confirm_key,
                        None
                    )

                    st.rerun()

        st.write("")