import streamlit as st
from database import db
from auth import logout
from html import escape

# ==========================================================
# HTML
# ==========================================================

def html(code):
    st.markdown(code, unsafe_allow_html=True)


# ==========================================================
# CARD
# ==========================================================

def card_start():

    html("""
<div class="idea-card">
""")

def card_end():

    html("""
</div>
""")


# ==========================================================
# SECTION
# ==========================================================

def section(title, icon="🌱"):

    html(f"""
<div style="
display:flex;
align-items:center;
gap:12px;
margin-top:10px;
margin-bottom:18px;
">

<div style="
font-size:30px;
">
{icon}
</div>

<div style="
font-size:25px;
font-weight:800;
color:#24324A;
">
{title}
</div>

</div>
""")


# ==========================================================
# HEADER
# ==========================================================

def render_header():

    profile = db.get_profile()

    level = profile["level"]
    exp = profile["exp"]

    max_exp = max(level * 100, 100)

    percent = exp / max_exp

    if percent > 1:
        percent = 1

    html(f"""

<div class="header-card">

<h1>

🌱 Idea Seed AI

</h1>

<p>

아이디어를 발명으로 키우는 연구 플랫폼

</p>

<div style="
display:flex;
justify-content:center;
gap:20px;
margin-top:15px;
font-size:18px;
">

<div>

🏆 Level <b>{level}</b>

</div>

<div>

⭐ {exp} / {max_exp} XP

</div>

</div>

</div>

""")

    st.progress(percent)


# ==========================================================
# TODAY CARD
# ==========================================================

def today_card():

    profile = db.get_profile()

    html(f"""

<div class="success-card">

<h3 style="margin-top:0">

🌱 오늘도 연구를 시작해볼까요?

</h3>

<p>

연구주제 <b>{profile['total_topics']}</b>개

&nbsp;&nbsp;&nbsp;

실패노트 <b>{profile['total_failures']}</b>개

&nbsp;&nbsp;&nbsp;

AI 대화 <b>{profile['total_chats']}</b>회

</p>

</div>

""")


# ==========================================================
# HOME MENU
# ==========================================================

def home_menu():

    section("메뉴", "🚀")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "🌰 씨앗보관함",
            key="menu_seeds",
            use_container_width=True
        ):
            st.session_state.page = "seeds"
            st.rerun()

        if st.button(
            "🌳 성장나무",
            key="menu_tree",
            use_container_width=True
        ):
            st.session_state.page = "tree"
            st.rerun()

        if st.button(
            "📕 실패노트",
            key="menu_failure",
            use_container_width=True
        ):
            st.session_state.page = "failure"
            st.rerun()

        if st.button(
            "🔬 연구노트",
            key="menu_research",
            use_container_width=True
        ):
            st.session_state.page = "research"
            st.rerun()

        if st.button(
            "📅 탐구로그",
            key="menu_timeline",
            use_container_width=True
        ):
            st.session_state.page = "timeline"
            st.rerun()

    with c2:

        if st.button(
            "🤖 AI 연구조교",
            key="menu_ai",
            use_container_width=True
        ):
            st.session_state.page = "mentor"
            st.rerun()

        if st.button(
            "🍎 열매마켓",
            key="menu_market",
            use_container_width=True
        ):
            st.session_state.page = "market"
            st.rerun()

        if st.button(
            "🔍 발전센터",
            key="menu_evaluation",
            use_container_width=True
        ):
            st.session_state.page = "evaluation"
            st.rerun()

        if st.button(
            "📁 포트폴리오",
            key="menu_portfolio",
            use_container_width=True
        ):
            st.session_state.page = "portfolio"
            st.rerun()

# ==========================================================
# PROFILE CARD
# ==========================================================

def profile_card():

    profile = db.get_profile()

    section("나의 연구원 정보", "🧒")

    html(f"""
<div class="idea-card">

<div style="
display:flex;
align-items:center;
gap:20px;
">

<div style="
font-size:72px;
line-height:1;
">
🧒
</div>

<div style="flex:1;">

<div style="
font-size:26px;
font-weight:800;
color:#24324A;
margin-bottom:6px;
">
{profile['nickname']}
</div>

<div style="
font-size:17px;
color:#6B7280;
margin-bottom:12px;
">
아이디어 연구원
</div>

<div style="
display:flex;
gap:18px;
flex-wrap:wrap;
font-size:16px;
">

<div>
🏆 레벨 <b>{profile['level']}</b>
</div>

<div>
⭐ 경험치 <b>{profile['exp']}</b>
</div>

</div>

</div>

</div>

</div>
""")


# ==========================================================
# DASHBOARD
# ==========================================================

def dashboard():

    data = db.dashboard()

    section("연구 현황", "📊")

    c1, c2, c3 = st.columns(3)

    with c1:

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
🌳
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{data['topics']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
연구주제
</div>

</div>
""")

    with c2:

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
🍎
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{data['finished']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
완성 연구
</div>

</div>
""")

    with c3:

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
📕
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{data['failures']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
실패노트
</div>

</div>
""")

    st.write("")

    c4, c5, c6 = st.columns(3)

    with c4:

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
🤖
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{data['chats']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
AI 대화
</div>

</div>
""")

    with c5:

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
⭐
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{data['average']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
평균 성장점수
</div>

</div>
""")

    with c6:

        profile = data["profile"]

        html(f"""
<div class="dashboard-card">

<div style="font-size:44px;">
🏆
</div>

<div style="
font-size:34px;
font-weight:900;
margin-top:8px;
">
{profile['level']}
</div>

<div style="
font-size:16px;
color:#6B7280;
">
현재 레벨
</div>

</div>
""")


# ==========================================================
# MISSION PANEL
# ==========================================================

def mission_panel():

    section("오늘의 미션", "🎯")

    missions = db.get_missions()

    if not missions:

        empty_card(
            "미션이 없어요.",
            "새로운 미션이 준비되면 여기에 표시돼요.",
            "🎯"
        )

        return

    for mission in missions:

        completed = int(mission["completed"]) == 1

        html(f"""
<div class="mission-card">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
gap:12px;
">

<div>

<div style="
font-size:18px;
font-weight:800;
color:#24324A;
">
{'✅' if completed else '🎯'} {mission['title']}
</div>

<div style="
font-size:14px;
color:#6B7280;
margin-top:5px;
">
보상 +{mission['reward']} XP
</div>

</div>

<div style="
font-size:30px;
">
{'🏆' if completed else '🌱'}
</div>

</div>

</div>
""")

        if not completed:

            if st.button(
                "미션 완료",
                key=f"mission_complete_{mission['id']}",
                use_container_width=True
            ):

                db.complete_mission(
                    mission["id"]
                )

                st.rerun()

        else:

            st.success("완료한 미션입니다.")


# ==========================================================
# BADGE PANEL
# ==========================================================

def badge_panel():

    section("나의 배지", "🏅")

    badges = db.get_badges()

    if not badges:

        empty_card(
            "아직 배지가 없어요.",
            "연구와 미션을 진행하면 새로운 배지를 얻을 수 있어요.",
            "🏅"
        )

        return

    cols = st.columns(3)

    for index, badge in enumerate(badges):

        unlocked = bool(badge["unlocked"])

        with cols[index % 3]:

            if unlocked:

                html(f"""
<div class="badge-card">

<div style="
font-size:48px;
text-align:center;
margin-bottom:10px;
">
{badge['icon']}
</div>

<div style="
font-size:18px;
font-weight:800;
text-align:center;
color:#24324A;
margin-bottom:6px;
">
{badge['name']}
</div>

<div style="
font-size:14px;
text-align:center;
color:#6B7280;
line-height:1.5;
">
{badge['description']}
</div>

<div style="
margin-top:12px;
text-align:center;
font-size:13px;
font-weight:700;
color:#16A34A;
">
획득 완료
</div>

</div>
""")

            else:

                html(f"""
<div class="badge-card" style="opacity:0.55;">

<div style="
font-size:48px;
text-align:center;
margin-bottom:10px;
">
🔒
</div>

<div style="
font-size:18px;
font-weight:800;
text-align:center;
color:#24324A;
margin-bottom:6px;
">
잠긴 배지
</div>

<div style="
font-size:14px;
text-align:center;
color:#6B7280;
line-height:1.5;
">
연구 활동을 계속하면 열 수 있어요.
</div>

<div style="
margin-top:12px;
text-align:center;
font-size:13px;
font-weight:700;
color:#9CA3AF;
">
미획득
</div>

</div>
""")


# ==========================================================
# STATISTIC CARD
# ==========================================================

def statistic_card():

    profile = db.get_profile()

    section("연구 통계", "📈")

    level = max(int(profile["level"]), 1)
    exp = max(int(profile["exp"]), 0)

    need_exp = level * 100
    progress = min(exp / need_exp, 1.0)

    html(f"""
<div class="idea-card">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:12px;
">

<div style="
font-size:19px;
font-weight:800;
color:#24324A;
">
🏆 레벨 {level}
</div>

<div style="
font-size:15px;
font-weight:700;
color:#6B7280;
">
{exp} / {need_exp} XP
</div>

</div>

</div>
""")

    st.progress(progress)

    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:

        html(f"""
<div class="dashboard-card">

<div style="font-size:36px;">
🌳
</div>

<div style="
font-size:28px;
font-weight:900;
margin-top:8px;
">
{profile['total_topics']}
</div>

<div style="
font-size:14px;
color:#6B7280;
">
전체 연구
</div>

</div>
""")

    with c2:

        html(f"""
<div class="dashboard-card">

<div style="font-size:36px;">
📕
</div>

<div style="
font-size:28px;
font-weight:900;
margin-top:8px;
">
{profile['total_failures']}
</div>

<div style="
font-size:14px;
color:#6B7280;
">
실패 기록
</div>

</div>
""")

    with c3:

        html(f"""
<div class="dashboard-card">

<div style="font-size:36px;">
🤖
</div>

<div style="
font-size:28px;
font-weight:900;
margin-top:8px;
">
{profile['total_chats']}
</div>

<div style="
font-size:14px;
color:#6B7280;
">
AI 대화
</div>

</div>
""")


# ==========================================================
# EMPTY CARD
# ==========================================================

def empty_card(title, message, icon="🌱"):

    html(f"""
<div class="empty-card">

<div style="
font-size:54px;
margin-bottom:12px;
">
{icon}
</div>

<div style="
font-size:21px;
font-weight:800;
color:#24324A;
margin-bottom:8px;
">
{title}
</div>

<div style="
font-size:15px;
color:#6B7280;
line-height:1.6;
">
{message}
</div>

</div>
""")


# ==========================================================
# LOADING CARD
# ==========================================================

def loading_card(text="불러오는 중..."):

    html(f"""
<div class="idea-card">

<div style="
display:flex;
align-items:center;
justify-content:center;
gap:12px;
font-size:17px;
font-weight:700;
color:#4B5563;
padding:12px;
">

<div style="font-size:30px;">
⏳
</div>

<div>
{text}
</div>

</div>

</div>
""")


# ==========================================================
# AI THINKING
# ==========================================================

def ai_thinking():

    html("""
<div class="idea-card">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div style="
font-size:34px;
">
🤖
</div>

<div>

<div style="
font-size:17px;
font-weight:800;
color:#24324A;
margin-bottom:4px;
">
AI 연구조교가 생각하고 있어요.
</div>

<div style="
font-size:14px;
color:#6B7280;
">
잠시만 기다려 주세요.
</div>

</div>

</div>

</div>
""")


# ==========================================================
# SUCCESS CARD
# ==========================================================

def success_card(message):

    html(f"""
<div class="success-card">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div style="
font-size:30px;
">
✅
</div>

<div style="
font-size:16px;
font-weight:700;
line-height:1.6;
">
{message}
</div>

</div>

</div>
""")


# ==========================================================
# ERROR CARD
# ==========================================================

def error_card(message):

    html(f"""
<div class="error-card">

<div style="
display:flex;
align-items:center;
gap:12px;
">

<div style="
font-size:30px;
">
⚠️
</div>

<div style="
font-size:16px;
font-weight:700;
line-height:1.6;
">
{message}
</div>

</div>

</div>
""")


# ==========================================================
# FRUIT MARKET
# ==========================================================

def market_page():

    html("""
<div class="header-card">
<h1>🍎 열매마켓</h1>
<p>완성한 연구 작품을 나누고 서로의 아이디어를 키워주세요.</p>
</div>
""")

    search_col, sort_col = st.columns([3, 1])

    with search_col:
        keyword = st.text_input(
            "작품 검색",
            placeholder="찾고 싶은 작품 이름을 입력하세요.",
            label_visibility="collapsed",
            key="market_search"
        )

    with sort_col:
        sort_label = st.selectbox(
            "정렬",
            ["최신순", "인기순"],
            label_visibility="collapsed",
            key="market_sort"
        )

    posts = db.get_market_posts(
        sort="popular" if sort_label == "인기순" else "latest",
        keyword=keyword
    )

    if not posts:
        empty_card(
            "아직 공개된 작품이 없어요.",
            "성장나무에서 열매를 완성한 뒤 작품을 공개해 보세요.",
            "🍎"
        )
        return

    for post in posts:
        post_id = int(post["id"])
        title = escape(str(post.get("title") or "이름 없는 작품"))
        fruit = escape(str(post.get("fruit") or "🍎"))
        nickname = escape(str(post.get("nickname") or "새싹 연구원"))
        description = escape(str(post.get("description") or "")).replace("\n", "<br>")
        like_count = int(post.get("like_count") or 0)
        comment_count = int(post.get("comment_count") or 0)

        html(f"""
<div class="topic-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:15px;">
        <div style="display:flex;gap:15px;align-items:center;">
            <div style="font-size:54px;">{fruit}</div>
            <div>
                <div style="font-size:22px;font-weight:900;color:#24324A;">{title}</div>
                <div style="font-size:14px;color:#6B7280;margin-top:4px;">🌱 {nickname} 연구원</div>
            </div>
        </div>
        <div style="background:#F1FBEF;padding:7px 12px;border-radius:999px;color:#2E7D32;font-weight:800;">
            완성 작품
        </div>
    </div>
    <div style="margin-top:15px;padding:15px;background:#F8FAFC;border-radius:15px;line-height:1.7;">
        {description or '작품 설명이 아직 없습니다.'}
    </div>
    <div style="margin-top:12px;color:#6B7280;font-size:14px;">
        ❤️ 좋아요 {like_count} &nbsp;&nbsp; 💬 댓글 {comment_count}
    </div>
</div>
""")

        with st.expander("📚 연구 과정 전체 보기"):
            details = db.get_market_post_details(post_id)
            detail_topic = details["topic"] or {}

            st.markdown("#### 📝 연구 메모")
            st.write(
                detail_topic.get("memo")
                or "작성된 연구 메모가 없습니다."
            )

            st.markdown("#### 📈 성장 기록")
            detail_score = int(detail_topic.get("score") or 0)
            stage_names = ["씨앗", "새싹", "나무", "꽃", "열매 완성"]
            st.progress(min(max(detail_score / 4, 0.0), 1.0))
            st.write(f"현재 성장 단계: **{detail_score}단계 · {stage_names[detail_score]}**")

            research_note = details.get("research_note")
            if research_note:
                st.markdown("#### 🔬 연구노트")
                st.markdown(f"**{escape(str(research_note['title']))}**")
                note_sections = [
                    ("❓ 탐구 질문", "research_question"),
                    ("🛠️ 탐구 과정", "process"),
                    ("📊 탐구 결과", "result"),
                    ("✅ 결론과 알게 된 점", "conclusion"),
                    ("🚀 다음 연구 계획", "next_plan")
                ]
                for label, field in note_sections:
                    value = research_note.get(field)
                    if value:
                        st.markdown(f"**{label}**")
                        st.write(value)

                note_attachments = details.get("research_attachments", [])
                if note_attachments:
                    st.markdown("**📎 연구노트 첨부 자료**")
                    attachment_cols = st.columns(3)
                    for attachment_index, attachment in enumerate(note_attachments):
                        with attachment_cols[attachment_index % 3]:
                            url = attachment.get("url")
                            if attachment["attachment_type"] in ("photo", "drawing") and url:
                                st.image(url, use_container_width=True)
                            if url:
                                st.link_button(
                                    attachment["original_name"],
                                    url,
                                    use_container_width=True
                                )

            st.markdown("#### 📕 실패노트")
            if not details["failures"]:
                st.caption("공유된 실패노트가 없습니다.")
            else:
                for failure in details["failures"]:
                    with st.container(border=True):
                        st.markdown(f"**📕 {escape(str(failure['title']))}**")
                        st.markdown("**😥 실패 원인**")
                        st.write(failure.get("reason") or "기록 없음")
                        st.markdown("**🔧 해결 방법**")
                        st.write(failure.get("solution") or "기록 없음")
                        st.markdown("**🌱 배운 점**")
                        st.write(failure.get("learned") or "기록 없음")

            st.markdown("#### 🤖 AI 연구조교 대화")
            if not details["chats"]:
                st.caption("공유된 AI 대화가 없습니다.")
            else:
                for chat in details["chats"]:
                    if chat["role"] == "user":
                        st.markdown(f"**🧒 질문**  \n{escape(str(chat['message']))}")
                    else:
                        st.markdown(f"**🤖 연구조교**  \n{escape(str(chat['message']))}")
                    st.divider()

        liked = db.has_liked(post_id)
        like_col, comment_col = st.columns([1, 3])

        with like_col:
            if st.button(
                "❤️ 좋아요 취소" if liked else "🤍 좋아요",
                key=f"market_like_{post_id}",
                use_container_width=True
            ):
                db.toggle_like(post_id)
                st.rerun()

        with comment_col:
            show_key = f"show_comments_{post_id}"
            if st.button(
                f"💬 댓글과 아이디어 보기 ({comment_count})",
                key=f"market_comments_button_{post_id}",
                use_container_width=True
            ):
                st.session_state[show_key] = not st.session_state.get(show_key, False)
                st.rerun()

        if st.session_state.get(f"show_comments_{post_id}", False):
            comments = db.get_market_comments(post_id)

            with st.container(border=True):
                if not comments:
                    st.caption("첫 번째 응원이나 아이디어를 남겨보세요.")

                current_user = st.session_state.get("auth_user", {})
                current_uid = current_user.get("id") if isinstance(current_user, dict) else None

                for comment in comments:
                    icon = "💡" if comment["comment_type"] == "idea" else "👏"
                    label = "아이디어 추가" if comment["comment_type"] == "idea" else "응원"
                    c1, c2 = st.columns([8, 1])
                    with c1:
                        st.markdown(
                            f"**{icon} {escape(str(comment['nickname']))} · {label}**  \n"
                            f"{escape(str(comment['content']))}"
                        )
                    with c2:
                        if str(comment["user_id"]) == str(current_uid):
                            if st.button("삭제", key=f"delete_market_comment_{comment['id']}"):
                                db.delete_market_comment(comment["id"])
                                st.rerun()

                with st.form(f"market_comment_form_{post_id}", clear_on_submit=True):
                    comment_type = st.radio(
                        "댓글 종류",
                        ["👏 응원 댓글", "💡 아이디어 추가"],
                        horizontal=True,
                        key=f"market_comment_type_{post_id}"
                    )
                    content = st.text_area(
                        "댓글",
                        max_chars=500,
                        placeholder="따뜻한 응원이나 작품을 발전시킬 아이디어를 적어주세요.",
                        key=f"market_comment_content_{post_id}"
                    )
                    submitted = st.form_submit_button("댓글 등록", use_container_width=True)

                if submitted:
                    if not content.strip():
                        st.warning("댓글 내용을 입력하세요.")
                    else:
                        db.add_market_comment(
                            post_id,
                            content,
                            "idea" if comment_type.startswith("💡") else "cheer"
                        )
                        st.rerun()

        st.divider()



# ==========================================================
# SIDEBAR
# ==========================================================

def render_sidebar():

    profile = db.get_profile()

    level = max(int(profile["level"]), 1)
    exp = max(int(profile["exp"]), 0)
    need_exp = level * 100
    progress = min(exp / need_exp, 1.0)

    with st.sidebar:

        html("""
<div style="
text-align:center;
font-size:70px;
margin-top:8px;
margin-bottom:4px;
">
🌱
</div>
""")

        html(f"""
<div style="
text-align:center;
font-size:24px;
font-weight:900;
color:#24324A;
margin-bottom:4px;
">
{profile['nickname']}
</div>

<div style="
text-align:center;
font-size:14px;
color:#6B7280;
margin-bottom:18px;
">
아이디어 연구원
</div>
""")

        html(f"""
<div class="idea-card">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
margin-bottom:10px;
">

<div style="
font-size:16px;
font-weight:800;
">
🏆 Level {level}
</div>

<div style="
font-size:14px;
font-weight:700;
color:#6B7280;
">
{exp} / {need_exp} XP
</div>

</div>

</div>
""")

        st.progress(progress)

        st.write("")

        if st.button(
            "🏠 홈",
            key="sidebar_home",
            use_container_width=True
        ):
            st.session_state.page = "home"
            st.rerun()

        if st.button(
            "🌰 씨앗보관함",
            key="sidebar_seeds",
            use_container_width=True
        ):
            st.session_state.page = "seeds"
            st.rerun()

        if st.button(
            "🌳 성장나무",
            key="sidebar_tree",
            use_container_width=True
        ):
            st.session_state.page = "tree"
            st.rerun()

        if st.button(
            "🤖 AI 연구조교",
            key="sidebar_mentor",
            use_container_width=True
        ):
            st.session_state.page = "mentor"
            st.rerun()

        if st.button(
            "📕 실패노트",
            key="sidebar_failure",
            use_container_width=True
        ):
            st.session_state.page = "failure"
            st.rerun()

        if st.button(
            "🔬 연구노트",
            key="sidebar_research",
            use_container_width=True
        ):
            st.session_state.page = "research"
            st.rerun()

        if st.button(
            "📅 탐구로그",
            key="sidebar_timeline",
            use_container_width=True
        ):
            st.session_state.page = "timeline"
            st.rerun()

        if st.button(
            "🔍 발전센터",
            key="sidebar_evaluation",
            use_container_width=True
        ):
            st.session_state.page = "evaluation"
            st.rerun()

        if st.button(
            "📁 포트폴리오",
            key="sidebar_portfolio",
            use_container_width=True
        ):
            st.session_state.page = "portfolio"
            st.rerun()

        if st.button(
            "🍎 열매마켓",
            key="sidebar_market",
            use_container_width=True
        ):
            st.session_state.page = "market"
            st.rerun()

        if st.button(
            "🚪 로그아웃",
            key="sidebar_logout",
            use_container_width=True
        ):
            logout()
            st.rerun()

        st.divider()

        html(f"""
<div class="idea-card">

<div style="
font-size:17px;
font-weight:800;
color:#24324A;
margin-bottom:12px;
">
📊 나의 연구 기록
</div>

<div style="
display:flex;
justify-content:space-between;
font-size:14px;
margin-bottom:8px;
">
<span>🌳 연구주제</span>
<b>{profile['total_topics']}</b>
</div>

<div style="
display:flex;
justify-content:space-between;
font-size:14px;
margin-bottom:8px;
">
<span>📕 실패노트</span>
<b>{profile['total_failures']}</b>
</div>

<div style="
display:flex;
justify-content:space-between;
font-size:14px;
">
<span>🤖 AI 대화</span>
<b>{profile['total_chats']}</b>
</div>

</div>
""")

        html("""
<div style="
margin-top:16px;
padding:14px;
border-radius:16px;
background:#ECFDF5;
font-size:14px;
line-height:1.6;
color:#166534;
text-align:center;
font-weight:700;
">
오늘도 새로운 아이디어를<br>
한 단계 키워보세요! 🌱
</div>
""")


# ==========================================================
# FOOTER
# ==========================================================

def footer():

    st.write("")

    st.divider()

    html("""
<div style="
text-align:center;
padding:8px 0 14px 0;
font-size:13px;
color:#9CA3AF;
line-height:1.7;
">
🌱 Idea Seed AI<br>
아이디어를 발명으로 키우는 어린이 연구 플랫폼
</div>
""")


# ==========================================================
# END
# ==========================================================
