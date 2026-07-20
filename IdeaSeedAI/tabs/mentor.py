import streamlit as st
from database import db

# OpenAI SDK
from openai import OpenAI

# =====================================
# API KEY
# =====================================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)


# =====================================
# AI 답변
# =====================================

def ask_ai(topic_name, question):

    system_prompt = f"""
너는 초등학생과 중학생을 위한 AI 연구조교이다.

현재 연구주제는

{topic_name}

이다.

항상

- 쉽고
- 친절하고
- 단계별로
- 창의적으로

설명한다.

답변 마지막에는

'다음으로 해볼 연구'

를 하나 추천한다.
"""

    response = client.chat.completions.create(

        model="gpt-4.1",

        messages=[

            {
                "role": "system",
                "content": system_prompt
            },

            {
                "role": "user",
                "content": question
            }

        ]

    )

    return response.choices[0].message.content


# =====================================
# 화면
# =====================================

def render():

    st.title("🤖 AI 연구조교")

    topics = db.get_topics()

    if len(topics) == 0:

        st.info("먼저 성장나무에서 연구주제를 만들어 주세요.")

        return

    topic = st.selectbox(

        "연구주제",

        topics,

        format_func=lambda x:
            f"{x['fruit']} {x['name']}"

    )

    st.divider()

    history = db.get_chat(topic["id"])

    for chat in history:

        with st.chat_message(chat["role"]):

            st.write(chat["message"])

    question = st.chat_input("무엇이 궁금한가요?")

    if question:

        db.save_chat(
            topic["id"],
            "user",
            question
        )

        with st.chat_message("user"):

            st.write(question)

        with st.spinner("AI 연구조교가 생각하는 중..."):

            answer = ask_ai(
                topic["name"],
                question
            )

        db.save_chat(
            topic["id"],
            "assistant",
            answer
        )

        with st.chat_message("assistant"):

            st.write(answer)

        st.rerun()