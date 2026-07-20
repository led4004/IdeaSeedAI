import streamlit as st
from database import db


def render():

    st.title("📕 실패노트")

    topics = db.get_topics()

    if len(topics) == 0:

        st.info("먼저 연구주제를 만들어 주세요.")

        return

    st.write("")

    st.subheader("✍ 새로운 실패노트")

    topic_name = st.selectbox(

        "연구주제",

        topics,

        format_func=lambda x: f"{x['fruit']} {x['name']}"

    )

    title = st.text_input("실패 제목")

    reason = st.text_area("왜 실패했나요?")

    solution = st.text_area("어떻게 해결할까요?")

    learned = st.text_area("이번 실패로 배운 점")

    if st.button(

        "💾 실패노트 저장",

        use_container_width=True

    ):

        if title.strip() == "":

            st.warning("제목을 입력하세요.")

        else:

            db.add_failure(

                topic_name["id"],

                title,

                reason,

                solution,

                learned

            )

            st.success("실패노트를 저장했습니다.")

            st.rerun()

    st.divider()

    st.subheader("📚 저장된 실패노트")

    failures = db.get_failures()

    if len(failures) == 0:

        st.info("아직 실패노트가 없습니다.")

        return

    for failure in failures:

        with st.expander(

            f"{failure['fruit']} {failure['topic_name']} - {failure['title']}"

        ):

            st.markdown("### 😥 실패 원인")

            st.write(failure["reason"])

            st.markdown("### 🔧 해결 방법")

            st.write(failure["solution"])

            st.markdown("### 🌱 배운 점")

            st.write(failure["learned"])

            if st.button(

                "🗑 삭제",

                key=f"delete_failure_{failure['id']}"

            ):

                db.delete_failure(

                    failure["id"]

                )

                st.success("삭제되었습니다.")

                st.rerun()