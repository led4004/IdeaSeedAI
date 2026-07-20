import streamlit as st
from database import db


FRUITS = {
    "🍎": "사과",
    "🍊": "귤",
    "🍇": "포도",
    "🍓": "딸기",
    "🍉": "수박",
    "🥝": "키위",
    "🍒": "체리",
    "🥥": "코코넛"
}


def render():

    st.title("🌳 아이디어 성장나무")

    st.write("")

    with st.expander("🌱 새로운 아이디어 심기", expanded=True):

        title = st.text_input(
            "아이디어 이름"
        )

        fruit = st.selectbox(
            "열매 선택",
            list(FRUITS.keys()),
            format_func=lambda x: f"{x} {FRUITS[x]}"
        )

        if st.button(
            "🌱 심기",
            use_container_width=True
        ):

            if title.strip() == "":

                st.warning("아이디어 이름을 입력하세요.")

            else:

                result = db.add_topic(
                    title,
                    fruit
                )

                if result is False:

                    st.error("이미 존재하는 아이디어입니다.")

                else:

                    st.success("새로운 아이디어를 심었습니다!")

                    st.rerun()

    st.divider()

    topics = db.get_topics()

    if len(topics) == 0:

        st.info("아직 심은 아이디어가 없습니다.")

        return

    for topic in topics:

        with st.container():

            st.markdown("---")

            c1, c2 = st.columns([6, 1])

            with c1:

                st.subheader(
                    f"{topic['fruit']} {topic['name']}"
                )

            with c2:

                if st.button(
                    "🗑",
                    key=f"delete_{topic['id']}"
                ):

                    db.delete_topic(
                        topic["id"]
                    )

                    st.rerun()

            score = st.slider(

                "성장 단계",

                0,

                4,

                value=topic["score"],

                key=f"score_{topic['id']}"

            )

            if score != topic["score"]:

                db.update_topic_score(
                    topic["id"],
                    score
                )

                st.rerun()

            memo = st.text_area(

                "연구 메모",

                value=topic["memo"] if topic["memo"] else "",

                key=f"memo_{topic['id']}"

            )

            if st.button(

                "💾 메모 저장",

                key=f"save_{topic['id']}"

            ):

                db.update_topic_memo(

                    topic["id"],

                    memo

                )

                st.success("저장되었습니다.")

            progress = score / 4

            st.progress(progress)

            if score == 0:

                st.caption("🌱 씨앗")

            elif score == 1:

                st.caption("🌿 새싹")

            elif score == 2:

                st.caption("🌳 나무")

            elif score == 3:

                st.caption("🌸 꽃")

            else:

                st.success("🍎 열매 완성!")