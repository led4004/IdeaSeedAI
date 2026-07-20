import streamlit as st
from html import escape
from database import db
from components import section, empty_card

FRUITS = {
    "🍎":"사과",
    "🍊":"귤",
    "🍇":"포도",
    "🍓":"딸기",
    "🍉":"수박",
    "🥝":"키위",
    "🍒":"체리",
    "🥥":"코코넛"
}


# ==========================================================
# TREE IMAGE
# ==========================================================

def draw_tree():

    topics = db.get_topics()
    completed_topics = [
        {
            "fruit": str(topic["fruit"]),
            "name": str(topic["name"])
        }
        for topic in topics
        if int(topic.get("score") or 0) >= 4
    ]

    fruit_positions = [
        (34, 18), (51, 13), (65, 24), (41, 36),
        (58, 39), (28, 43), (70, 47), (48, 54),
        (37, 61), (61, 62), (24, 29), (76, 35)
    ]

    visible_topics = completed_topics[:len(fruit_positions)]
    fruit_html = "".join(
        f"""
<span style="
position:absolute;
left:{left}%;
top:{top}%;
transform:translate(-50%, -50%);
font-size:34px;
z-index:3;
filter:drop-shadow(0 3px 3px rgba(0,0,0,0.18));
cursor:help;
" title="{escape(topic['name'], quote=True)}">{topic['fruit']}</span>
"""
        for topic, (left, top) in zip(visible_topics, fruit_positions)
    )

    extra_count = max(len(completed_topics) - len(visible_topics), 0)
    extra_html = (
        f"""
<div style="
position:absolute;
right:8%;
bottom:14%;
background:#FFFFFF;
border:2px solid #DDF3D8;
border-radius:999px;
padding:5px 10px;
font-size:14px;
font-weight:800;
color:#2E7D32;
z-index:4;
">+{extra_count}</div>
"""
        if extra_count > 0 else ""
    )

    fruit_message = (
        f"완성한 연구 열매 <b>{len(completed_topics)}</b>개가 달렸어요!"
        if completed_topics
        else "첫 연구를 완성하면 나무에 열매가 달려요!"
    )

    name_tags_html = "".join(
        f"""
<span style="
display:inline-flex;
align-items:center;
gap:6px;
background:#F1FBEF;
border:1px solid #D9EFD4;
border-radius:999px;
padding:7px 12px;
font-size:14px;
font-weight:700;
color:#245C2B;
">{topic['fruit']} {escape(topic['name'])}</span>
"""
        for topic in completed_topics
    )

    completed_list_html = (
        f"""
<div style="margin-top:18px;">
<div style="font-size:14px;font-weight:800;color:#4B5563;margin-bottom:10px;">🍎 완성한 아이디어</div>
<div style="display:flex;justify-content:center;flex-wrap:wrap;gap:8px;">{name_tags_html}</div>
</div>
"""
        if completed_topics else ""
    )

    st.markdown(f"""

<div class="tree-card">

<div class="tree-title">

🌳 나의 성장나무

</div>

<div style="
position:relative;
width:330px;
height:215px;
margin:0 auto;
">

<div style="
position:absolute;
left:50%;
top:50%;
transform:translate(-50%, -50%);
font-size:170px;
line-height:1;
z-index:1;
">

🌳

</div>

{fruit_html}
{extra_html}

</div>

<p>

{fruit_message}<br>
열매가 많아질수록 멋진 발명가가 됩니다!

</p>

{completed_list_html}

</div>

""",unsafe_allow_html=True)


# ==========================================================
# ADD TOPIC
# ==========================================================

def add_topic():

    section("새로운 아이디어 심기","🌱")

    with st.container():

        title=st.text_input(

            "아이디어 이름",

            placeholder="예) 바다를 청소하는 로봇"

        )

        fruit=st.selectbox(

            "열매",

            list(FRUITS.keys()),

            format_func=lambda x:f"{x} {FRUITS[x]}"

        )

        if st.button(

            "🌱 씨앗 심기",

            use_container_width=True

        ):

            if title.strip()=="":

                st.warning("아이디어 이름을 입력하세요.")

                return

            result=db.add_topic(

                title,

                fruit

            )

            if result is False:

                st.error("이미 있는 아이디어입니다.")

            else:

                st.success("새로운 씨앗을 심었습니다! 🌱")

                st.rerun()


# ==========================================================
# RENDER
# ==========================================================

def render():

    draw_tree()

    st.write("")

    add_topic()

    st.divider()

    topics=db.get_topics()

    if len(topics)==0:

        empty_card(

            "아직 씨앗이 없어요",

            "첫 번째 아이디어를 심어보세요.",

            "🌱"

        )

        return

    section("나의 연구","🍎")


    cols = st.columns(2)

    for index, topic in enumerate(topics):

        with cols[index % 2]:

            growth = db.refresh_topic_growth(topic["id"])
            score = int(growth["score"])
            memo = topic["memo"] or ""

            if score <= 0:
                stage_icon = "🌱"
                stage_name = "씨앗"
            elif score == 1:
                stage_icon = "🌿"
                stage_name = "새싹"
            elif score == 2:
                stage_icon = "🌳"
                stage_name = "나무"
            elif score == 3:
                stage_icon = "🌸"
                stage_name = "꽃"
            else:
                stage_icon = topic["fruit"]
                stage_name = "열매 완성"

            st.markdown(
                f"""
<div class="topic-card">

<div style="
display:flex;
justify-content:space-between;
align-items:center;
gap:12px;
">

<div>

<div class="topic-fruit">

{stage_icon}

</div>

<div class="topic-title">

{topic["name"]}

</div>

</div>

<div style="
background:#F1FBEF;
padding:8px 12px;
border-radius:999px;
font-weight:700;
color:#2E7D32;
white-space:nowrap;
">

{stage_name}

</div>

</div>

<div class="topic-score">

성장도 {score} / 4

</div>

</div>
""",
                unsafe_allow_html=True
            )

            st.progress(min(max(score / 4, 0.0), 1.0))

            st.caption("성장 단계는 연구 활동에 따라 자동으로 올라갑니다.")

            memo_check = "✅" if growth["memo_done"] else "⬜"
            chat2_check = "✅" if growth["ai_questions"] >= 2 else "⬜"
            failure_check = "✅" if growth["failure_done"] else "⬜"
            chat4_check = "✅" if growth["ai_questions"] >= 4 else "⬜"
            detail_check = "✅" if growth["failure_complete"] else "⬜"

            st.markdown(
                f"""
{memo_check} 연구 메모 작성  
{chat2_check} AI 연구조교 질문 2회 ({growth['ai_questions']}회)  
{failure_check} 실패노트 1개 작성  
{chat4_check} AI 연구조교 질문 4회 ({growth['ai_questions']}회)  
{detail_check} 실패 원인·해결 방법·배운 점 모두 기록
"""
            )

            new_memo = st.text_area(
                "연구 메모",
                value=memo,
                placeholder="오늘 한 일, 새로 알게 된 점, 다음 실험 계획을 적어보세요.",
                key=f"memo_{topic['id']}"
            )

            c1, c2 = st.columns([4, 1])

            with c1:

                if st.button(
                    "💾 메모 저장",
                    key=f"save_{topic['id']}",
                    use_container_width=True
                ):

                    db.update_topic_memo(
                        topic["id"],
                        new_memo
                    )

                    st.success("메모를 저장했습니다.")

            with c2:

                if st.button(
                    "🗑️",
                    key=f"delete_{topic['id']}",
                    use_container_width=True
                ):

                    st.session_state[
                        f"confirm_delete_{topic['id']}"
                    ] = True

                    st.rerun()

            if st.session_state.get(
                f"confirm_delete_{topic['id']}",
                False
            ):

                st.warning(
                    f"'{topic['name']}' 아이디어를 정말 삭제할까요?"
                )

                yes_col, no_col = st.columns(2)

                with yes_col:

                    if st.button(
                        "네, 삭제",
                        key=f"confirm_yes_{topic['id']}",
                        use_container_width=True
                    ):

                        db.delete_topic(
                            topic["id"]
                        )

                        st.session_state.pop(
                            f"confirm_delete_{topic['id']}",
                            None
                        )

                        st.rerun()

                with no_col:

                    if st.button(
                        "취소",
                        key=f"confirm_no_{topic['id']}",
                        use_container_width=True
                    ):

                        st.session_state.pop(
                            f"confirm_delete_{topic['id']}",
                            None
                        )

                        st.rerun()

            if score >= 4:

                st.success(
                    f"{topic['fruit']} 멋진 열매가 완성됐어요!"
                )

                published = db.is_topic_published(topic["id"])

                if published:
                    if st.button(
                        "🍎 열매마켓 공개 취소",
                        key=f"unpublish_{topic['id']}",
                        use_container_width=True
                    ):
                        db.unpublish_topic(topic["id"])
                        st.success("열매마켓 공개를 취소했습니다.")
                        st.rerun()
                else:
                    if st.button(
                        "🍎 열매마켓에 작품 공개",
                        key=f"publish_{topic['id']}",
                        use_container_width=True
                    ):
                        db.publish_topic(topic["id"])
                        st.success("열매마켓에 작품을 공개했습니다!")
                        st.rerun()

            st.write("")


