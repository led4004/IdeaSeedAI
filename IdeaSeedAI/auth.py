import streamlit as st
import os
import hashlib
import re
from supabase import create_client


def _config():
    env_url = os.getenv("SUPABASE_URL", "").strip()
    env_key = os.getenv("SUPABASE_ANON_KEY", "").strip()

    if env_url and env_key:
        return env_url, env_key

    try:
        return st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"]
    except Exception:
        return "", ""


def _admin_key():
    key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if key:
        return key
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if key:
        return key
    try:
        return str(st.secrets.get("SUPABASE_SECRET_KEY", "")).strip()
    except Exception:
        return ""


def initialize_auth():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_email" not in st.session_state:
        st.session_state.auth_email = ""
    if "supabase_client" not in st.session_state:
        url, key = _config()
        st.session_state.supabase_client = create_client(url, key) if url and key else None


def is_configured():
    url, key = _config()
    return bool(url and key)


def is_logged_in():
    return st.session_state.get("auth_user") is not None


def _login_email(login_id):
    normalized = login_id.strip().casefold()
    # 이메일의 @ 앞부분은 최대 64자입니다.
    # 접두사까지 포함해 제한을 넘지 않도록 해시를 48자로 줄입니다.
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:48]
    return f"u_{digest}@users.ideaseed.app"


def _valid_login_id(login_id):
    return bool(re.fullmatch(r"[A-Za-z0-9가-힣_]{4,20}", login_id.strip()))


def _normalize_login_id(login_id):
    return login_id.strip().casefold()


def is_login_id_available(login_id):
    if not _valid_login_id(login_id):
        return False
    response = st.session_state.supabase_client.rpc(
        "is_login_id_available",
        {"candidate": _normalize_login_id(login_id)}
    ).execute()
    return bool(response.data)


def login(login_id, password):
    client = st.session_state.supabase_client
    email = _login_email(login_id)
    response = client.auth.sign_in_with_password({"email": email, "password": password})
    st.session_state.auth_user = {
        "id": str(response.user.id), "login_id": login_id.strip()
    }
    st.session_state.auth_email = email
    return response


def signup(login_id, password, nickname):
    url, _ = _config()
    admin_key = _admin_key()

    if not admin_key:
        raise RuntimeError(
            "SUPABASE_SECRET_KEY가 설정되지 않았습니다. "
            "학생 아이디 가입에는 Supabase Secret key가 필요합니다."
        )

    admin_client = create_client(url, admin_key)
    email = _login_email(login_id)
    response = admin_client.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {
            "nickname": nickname.strip()[:20],
            "login_id": _normalize_login_id(login_id)
        }
    })

    if not response.user:
        raise RuntimeError("학생 계정을 생성하지 못했습니다.")

    return login(login_id, password)


def logout():
    client = st.session_state.get("supabase_client")
    if client:
        client.auth.sign_out()
    for key in ("auth_user", "auth_email", "openai_api_key",
                "api_key_input", "api_key_verified"):
        st.session_state.pop(key, None)
    st.session_state.page = "home"
    initialize_auth()


def render_login():
    st.markdown("""
    <style>
    div[data-testid="stButton"] button p,
    div[data-testid="stFormSubmitButton"] button p {
        color: white !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-card">
        <h1>🌱 Idea Seed AI</h1>
        <p>아이디어를 발명으로 키우는 연구 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)

    if not is_configured():
        st.error("Supabase 설정이 없습니다. .streamlit/secrets.toml을 설정해 주세요.")
        st.code('SUPABASE_URL = "https://프로젝트.supabase.co"\nSUPABASE_ANON_KEY = "키"')
        return

    login_tab, signup_tab = st.tabs(["🔐 로그인", "🌱 새 연구원 가입"])

    with login_tab:
        with st.form("login_form"):
            login_id = st.text_input("아이디", placeholder="예: isaac101")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", use_container_width=True)
        if submitted:
            if not login_id.strip() or not password:
                st.warning("아이디와 비밀번호를 입력하세요.")
            else:
                try:
                    login(login_id, password)
                    st.rerun()
                except Exception:
                    st.error("로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요.")

    with signup_tab:
        st.caption("아이디에는 영문, 숫자, 한글, 밑줄(_)만 사용할 수 있습니다.")

        login_id = st.text_input(
            "아이디 (4~20자)",
            key="signup_login_id",
            max_chars=20,
            placeholder="예: isaac101"
        )

        if st.button(
            "🔎 아이디 중복 확인",
            key="check_login_id",
            use_container_width=True
        ):
            st.session_state.checked_login_id = None
            st.session_state.login_id_available = False

            if not _valid_login_id(login_id):
                st.warning("아이디는 영문, 숫자, 한글, 밑줄로 4~20자 입력하세요.")
            else:
                try:
                    available = is_login_id_available(login_id)
                    st.session_state.checked_login_id = _normalize_login_id(login_id)
                    st.session_state.login_id_available = available
                    if available:
                        st.success("사용할 수 있는 아이디입니다.")
                    else:
                        st.error("이미 사용 중인 아이디입니다.")
                except Exception as error:
                    st.error(f"아이디 확인 오류: {error}")

        checked_id = st.session_state.get("checked_login_id")
        if checked_id and checked_id != _normalize_login_id(login_id):
            st.info("아이디를 변경했습니다. 중복 확인을 다시 해주세요.")

        with st.form("signup_form"):
            nickname = st.text_input("닉네임", max_chars=20)
            password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
            password_check = st.text_input("비밀번호 확인", type="password")
            submitted = st.form_submit_button("가입하기", use_container_width=True)
        if submitted:
            if len(nickname.strip()) < 2:
                st.warning("닉네임을 2자 이상 입력하세요.")
            elif not _valid_login_id(login_id):
                st.warning("아이디는 영문, 숫자, 한글, 밑줄로 4~20자 입력하세요.")
            elif (
                st.session_state.get("checked_login_id") != _normalize_login_id(login_id)
                or not st.session_state.get("login_id_available", False)
            ):
                st.warning("아이디 중복 확인을 먼저 해주세요.")
            elif len(password) < 6:
                st.warning("비밀번호는 6자 이상이어야 합니다.")
            elif password != password_check:
                st.warning("비밀번호가 서로 다릅니다.")
            else:
                try:
                    result = signup(login_id, password, nickname)
                    if result.session:
                        st.session_state.pop("checked_login_id", None)
                        st.session_state.pop("login_id_available", None)
                        st.rerun()
                except Exception as error:
                    error_text = str(error)
                    if "already" in error_text.lower() or "registered" in error_text.lower():
                        st.error("이미 사용 중인 아이디입니다.")
                    elif "signup" in error_text.lower() and "disabled" in error_text.lower():
                        st.error("Supabase에서 신규 가입이 꺼져 있습니다.")
                    elif "rate" in error_text.lower():
                        st.error("가입 요청이 너무 많습니다. 잠시 후 다시 시도하세요.")
                    else:
                        st.error(f"가입 오류: {error_text}")
