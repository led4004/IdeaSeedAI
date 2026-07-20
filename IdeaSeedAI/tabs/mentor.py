import streamlit as st
import os
from openai import OpenAI

from database import db
from components import (
    section,
    empty_card,
    ai_thinking,
    success_card,
    error_card,
)


# ============================================================
# 기본 설정
# ============================================================

MODEL_NAME = "gpt-4.1-mini"

SYSTEM_PROMPT = """
너는 초등학생과 중학생의 발명 및 연구 활동을 돕는
친절한 AI 연구조교이다.

다음 원칙을 지켜서 답변한다.

1. 학생이 이해하기 쉬운 한국어를 사용한다.
2. 어려운 전문용어는 쉬운 말로 풀어서 설명한다.
3. 답을 바로 정해 주기보다 학생이 스스로 생각하도록 돕는다.
4. 아이디어를 구체적인 실험이나 제작 과정으로 발전시킨다.
5. 위험한 실험은 권하지 않는다.
6. 답변은 너무 길지 않게 작성한다.
7. 가능하면 준비물, 실험 방법, 관찰 항목을 구분해서 설명한다.
"""


# ============================================================
# 세션 상태 초기화
# ============================================================

def initialize_mentor_state():

    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""

    if "api_key_input" not in st.session_state:
        st.session_state.api_key_input = ""

    if "api_key_verified" not in st.session_state:
        st.session_state.api_key_verified = False


# ============================================================
# OpenAI 클라이언트 생성
# ============================================================

def get_openai_client():

    api_key = get_active_api_key()

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key
    )


def get_shared_api_key():

    env_key = os.getenv("OPENAI_API_KEY", "").strip()

    if env_key:
        return env_key

    try:
        return str(
            st.secrets.get("OPENAI_API_KEY", "")
        ).strip()
    except Exception:
        return ""


def get_active_api_key():

    personal_key = st.session_state.get(
        "openai_api_key",
        ""
    ).strip()

    return personal_key or get_shared_api_key()


def has_api_key():

    return bool(get_active_api_key())


# ============================================================
# API 키 입력 화면
# ============================================================

def render_api_key_panel():

    if get_shared_api_key():

        section(
            "AI 연구조교 이용 안내",
            "🔑"
        )

        success_card(
            "테스트용 공용 API 키가 연결되어 있습니다. "
            "학생은 별도의 API 키를 입력하지 않아도 됩니다."
        )

        return

    section(
        "내 OpenAI API 키",
        "🔑"
    )

    st.caption(
        "입력한 키는 현재 실행 중인 세션에서만 사용하며 "
        "데이터베이스나 파일에 저장하지 않습니다."
    )

    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        key="api_key_input",
        placeholder="sk- 또는 sk-proj-로 시작하는 API 키를 입력하세요.",
        help="입력한 키는 화면에서 가려집니다."
    )

    left, right = st.columns(2)

    with left:

        if st.button(
            "🔑 API 키 적용",
            key="save_api_key",
            use_container_width=True
        ):

            cleaned_key = api_key_input.strip()

            if not cleaned_key:

                st.session_state.api_key_verified = False

                error_card(
                    "API 키를 입력해 주세요."
                )

            elif not cleaned_key.startswith("sk-"):

                st.session_state.api_key_verified = False

                error_card(
                    "OpenAI API 키 형식을 확인해 주세요."
                )

            else:

                st.session_state.openai_api_key = cleaned_key
                st.session_state.api_key_verified = True

                success_card(
                    "API 키가 현재 세션에 적용되었습니다."
                )

                st.rerun()

    with right:

        if st.button(
            "🗑️ API 키 지우기",
            key="remove_api_key",
            use_container_width=True
        ):

            st.session_state.openai_api_key = ""
            st.session_state.api_key_input = ""
            st.session_state.api_key_verified = False

            st.rerun()

    if st.session_state.openai_api_key:

        st.success(
            "✅ API 키가 현재 세션에 등록되어 있습니다."
        )

    else:

        st.warning(
            "AI 연구조교를 사용하려면 자신의 OpenAI API 키를 입력하세요."
        )


# ============================================================
# AI 질문
# ============================================================

def ask_ai(
    topic_name,
    question,
    chat_history
):

    client = get_openai_client()

    if client is None:
        raise ValueError(
            "OpenAI API 키가 등록되어 있지 않습니다."
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": (
                f"학생이 현재 연구하고 있는 주제는 "
                f"'{topic_name}'이다."
            )
        }
    ]

    for chat in chat_history[-10:]:

        role = chat["role"]

        if role not in [
            "user",
            "assistant"
        ]:
            continue

        messages.append(
            {
                "role": role,
                "content": chat["message"]
            }
        )

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7
    )

    answer = response.choices[0].message.content

    if not answer:
        return "AI가 답변을 만들지 못했습니다. 다시 질문해 주세요."

    return answer.strip()


# ============================================================
# 오류 문구 변환
# ============================================================

def get_error_message(error):

    text = str(error).lower()

    if (
        "incorrect api key" in text
        or "invalid_api_key" in text
        or "401" in text
    ):
        return (
            "API 키가 올바르지 않습니다. "
            "키를 다시 확인해 주세요."
        )

    if (
        "insufficient_quota" in text
        or "quota" in text
        or "billing" in text
    ):
        return (
            "API 사용 한도나 결제 설정을 확인해 주세요."
        )

    if (
        "rate limit" in text
        or "429" in text
    ):
        return (
            "요청이 너무 많거나 사용 한도에 도달했습니다. "
            "잠시 후 다시 시도해 주세요."
        )

    if (
        "connection" in text
        or "timeout" in text
    ):
        return (
            "OpenAI 서버 연결에 실패했습니다. "
            "인터넷 연결을 확인하고 다시 시도해 주세요."
        )

    return f"AI 호출 중 오류가 발생했습니다: {error}"


# ============================================================
# AI 연구조교 헤더
# ============================================================

def mentor_header():

    st.markdown(
        """
<div class="header-card">

<h2 style="margin-top:0;">
🤖 AI 연구조교
</h2>

<p style="margin-bottom:0;">
연구 아이디어, 실험 방법, 준비물 등을 질문해 보세요.
</p>

</div>
""",
        unsafe_allow_html=True
    )


# ============================================================
# 대화 내용 출력
# ============================================================

def render_chat_history(chat_history):

    if not chat_history:

        empty_card(
            "아직 대화가 없어요.",
            "연구조교에게 첫 질문을 해보세요.",
            "🤖"
        )

        return

    chat_box = st.container(
        height=480
    )

    with chat_box:

        for chat in chat_history:

            role = chat["role"]
            message = chat["message"]

            if role == "user":

                with st.chat_message(
                    "user",
                    avatar="🧒"
                ):
                    st.write(message)

            else:

                with st.chat_message(
                    "assistant",
                    avatar="🤖"
                ):
                    st.write(message)


# ============================================================
# 빠른 질문
# ============================================================

def render_quick_questions(
    topic,
    chat_history
):

    section(
        "빠른 질문",
        "💡"
    )

    questions = [
        "이 아이디어가 실제로 가능할까?",
        "어떤 실험을 하면 좋을까?",
        "필요한 준비물을 알려줘.",
        "이 아이디어를 더 발전시키는 방법을 알려줘."
    ]

    columns = st.columns(2)

    for index, question in enumerate(questions):

        with columns[index % 2]:

            if st.button(
                question,
                key=f"quick_question_{index}",
                use_container_width=True,
                    disabled=not has_api_key()
            ):

                process_question(
                    topic,
                    question,
                    chat_history
                )


# ============================================================
# 질문 처리
# ============================================================

def process_question(
    topic,
    question,
    chat_history
):

    if not has_api_key():

        error_card(
            "먼저 자신의 OpenAI API 키를 입력해 주세요."
        )

        return

    db.save_chat(
        topic["id"],
        "user",
        question
    )

    with st.spinner(
        "AI 연구조교가 답변을 만들고 있어요..."
    ):

        ai_thinking()

        try:

            answer = ask_ai(
                topic["name"],
                question,
                chat_history
            )

        except Exception as error:

            error_card(
                get_error_message(error)
            )

            return

    db.save_chat(
        topic["id"],
        "assistant",
        answer
    )

    st.rerun()


# ============================================================
# 메인 화면
# ============================================================

def render():

    initialize_mentor_state()

    mentor_header()

    render_api_key_panel()

    st.divider()

    topics = db.get_topics()

    if not topics:

        empty_card(
            "연구주제가 없어요.",
            "성장나무에서 연구주제를 먼저 추가해 주세요.",
            "🌱"
        )

        return

    section(
        "연구주제 선택",
        "🌳"
    )

    topic_names = [
        topic["name"]
        for topic in topics
    ]

    selected_name = st.selectbox(
        "AI와 대화할 연구주제",
        topic_names,
        key="mentor_topic_select"
    )

    topic = next(
        topic
        for topic in topics
        if topic["name"] == selected_name
    )

    chat_history = db.get_chat(
        topic["id"]
    )

    section(
        f"{topic['name']} 연구 대화",
        "💬"
    )

    render_chat_history(
        chat_history
    )

    render_quick_questions(
        topic,
        chat_history
    )

    prompt = st.chat_input(
        "연구조교에게 질문해 보세요.",
        disabled=not has_api_key()
    )

    if prompt:

        process_question(
            topic,
            prompt,
            chat_history
        )
