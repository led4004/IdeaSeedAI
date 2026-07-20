import base64
import html
import io
import re
from datetime import datetime
from urllib.request import Request, urlopen

import streamlit as st
from PIL import Image

from database import db
from components import section, empty_card, success_card, error_card

try:
    from streamlit_drawable_canvas import st_canvas
except Exception:
    st_canvas = None


def research_header():
    st.markdown("""
<div class="header-card">
<h1>🔬 연구노트</h1>
<p>탐구 과정과 결과를 체계적으로 기록하고 포트폴리오로 완성해 보세요.</p>
</div>
""", unsafe_allow_html=True)


def render_ai_history(topic_id):
    chats = db.get_chat(topic_id)
    if not chats:
        st.caption("AI 연구조교와 나눈 대화가 아직 없습니다.")
        return
    with st.expander(f"🤖 AI 질문과 답변 자동 반영 ({len(chats)}개 메시지)"):
        for chat in chats:
            if chat["role"] == "user":
                st.markdown(f"**🧒 질문**  \n{chat['message']}")
            else:
                st.markdown(f"**🤖 연구조교 답변**  \n{chat['message']}")
            st.divider()


def render_note_form(topic):
    topic_id = int(topic["id"])
    note = db.get_research_note(topic_id)

    section("연구 내용 정리", "📝")
    render_ai_history(topic_id)

    with st.form(f"research_note_form_{topic_id}"):
        title = st.text_input(
            "연구노트 제목",
            value=(note or {}).get("title") or f"{topic['name']} 연구노트",
            max_chars=120
        )
        research_question = st.text_area(
            "탐구 질문",
            value=(note or {}).get("research_question") or "",
            placeholder="이 연구에서 알아보고 싶은 것은 무엇인가요?"
        )
        process = st.text_area(
            "탐구 과정",
            value=(note or {}).get("process") or "",
            placeholder="준비물, 제작 과정, 실험 방법을 순서대로 적어보세요.",
            height=160
        )
        result = st.text_area(
            "탐구 결과",
            value=(note or {}).get("result") or "",
            placeholder="관찰한 내용과 측정 결과를 적어보세요.",
            height=140
        )
        conclusion = st.text_area(
            "결론과 알게 된 점",
            value=(note or {}).get("conclusion") or "",
            placeholder="결과를 통해 알게 된 점을 정리해 보세요.",
            height=140
        )
        next_plan = st.text_area(
            "다음 연구 계획",
            value=(note or {}).get("next_plan") or "",
            placeholder="다음에 보완하거나 새로 실험할 내용을 적어보세요."
        )

        include_ai = st.checkbox(
            "AI 연구조교 질문과 답변을 연구노트에 포함",
            value=bool((note or {}).get("include_ai", True))
        )
        is_portfolio = st.checkbox(
            "📁 나의 포트폴리오에 추가",
            value=bool((note or {}).get("is_portfolio", False))
        )
        is_public = st.checkbox(
            "🌐 열매마켓 공개 작품에서 연구노트도 함께 공유",
            value=bool((note or {}).get("is_public", False)),
            help="성장나무에서 작품도 열매마켓에 공개해야 다른 학생이 볼 수 있습니다."
        )

        submitted = st.form_submit_button(
            "💾 연구노트 저장" if not note else "💾 수정 내용 저장",
            use_container_width=True
        )

    if submitted:
        if not title.strip():
            st.warning("연구노트 제목을 입력하세요.")
        else:
            db.save_research_note(topic_id, {
                "title": title,
                "research_question": research_question,
                "process": process,
                "result": result,
                "conclusion": conclusion,
                "next_plan": next_plan,
                "include_ai": include_ai,
                "is_portfolio": is_portfolio,
                "is_public": is_public
            })
            st.success("연구노트를 저장했습니다! 🔬")
            st.rerun()

    return db.get_research_note(topic_id)


def upload_files(note, topic_id):
    section("첨부 자료", "📎")

    photo_tab, file_tab, drawing_tab = st.tabs([
        "📷 사진", "📄 파일", "🎨 그림"
    ])

    with photo_tab:
        photos = st.file_uploader(
            "연구 사진 추가",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key=f"research_photos_{topic_id}"
        )
        if st.button("📷 선택한 사진 저장", key=f"save_photos_{topic_id}",
                     use_container_width=True):
            if not photos:
                st.warning("저장할 사진을 선택하세요.")
            else:
                for photo in photos:
                    db.upload_research_attachment(
                        note["id"], topic_id, photo.name, photo.getvalue(),
                        photo.type, "photo"
                    )
                st.success(f"사진 {len(photos)}장을 저장했습니다.")
                st.rerun()

    with file_tab:
        files = st.file_uploader(
            "연구 자료 파일 추가",
            type=["pdf", "doc", "docx", "hwp", "hwpx", "txt", "csv", "xlsx", "zip"],
            accept_multiple_files=True,
            key=f"research_files_{topic_id}"
        )
        if st.button("📄 선택한 파일 저장", key=f"save_files_{topic_id}",
                     use_container_width=True):
            if not files:
                st.warning("저장할 파일을 선택하세요.")
            else:
                for file in files:
                    db.upload_research_attachment(
                        note["id"], topic_id, file.name, file.getvalue(),
                        file.type, "file"
                    )
                st.success(f"파일 {len(files)}개를 저장했습니다.")
                st.rerun()

    with drawing_tab:
        if st_canvas is None:
            st.warning("그림판 구성요소를 불러오지 못했습니다. 그림 파일을 사진 탭에서 올려주세요.")
        else:
            tool_col, width_col, color_col = st.columns(3)
            with tool_col:
                mode = st.selectbox(
                    "도구", ["freedraw", "line", "rect", "circle"],
                    format_func=lambda x: {
                        "freedraw": "자유 그리기", "line": "선",
                        "rect": "사각형", "circle": "원"
                    }[x], key=f"canvas_mode_{topic_id}"
                )
            with width_col:
                stroke_width = st.slider(
                    "선 굵기", 1, 20, 3, key=f"canvas_width_{topic_id}"
                )
            with color_col:
                stroke_color = st.color_picker(
                    "선 색상", "#24324A", key=f"canvas_color_{topic_id}"
                )

            canvas = st_canvas(
                fill_color="rgba(125, 211, 152, 0.25)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="#FFFFFF",
                height=420,
                width=700,
                drawing_mode=mode,
                display_toolbar=True,
                update_streamlit=True,
                key=f"research_canvas_{topic_id}"
            )

            if st.button("🎨 그린 그림 저장", key=f"save_drawing_{topic_id}",
                         use_container_width=True):
                if canvas.image_data is None:
                    st.warning("먼저 그림을 그려주세요.")
                else:
                    image = Image.fromarray(canvas.image_data.astype("uint8"), "RGBA")
                    buffer = io.BytesIO()
                    image.save(buffer, format="PNG")
                    db.upload_research_attachment(
                        note["id"], topic_id,
                        f"research_drawing_{topic_id}.png",
                        buffer.getvalue(), "image/png", "drawing"
                    )
                    st.success("그림을 연구노트에 저장했습니다.")
                    st.rerun()


def render_saved_attachments(note):
    attachments = db.get_research_attachments(note["id"], with_urls=True)
    if not attachments:
        return

    section("저장된 첨부 자료", "🗂️")
    cols = st.columns(3)

    for index, attachment in enumerate(attachments):
        with cols[index % 3]:
            with st.container(border=True):
                url = attachment.get("url")
                if attachment["attachment_type"] in ("photo", "drawing") and url:
                    st.image(url, use_container_width=True)
                else:
                    st.markdown("### 📄")
                st.caption(attachment["original_name"])
                if url:
                    st.link_button("열기 또는 다운로드", url, use_container_width=True)
                if st.button(
                    "🗑️ 삭제",
                    key=f"delete_attachment_{attachment['id']}",
                    use_container_width=True
                ):
                    db.delete_research_attachment(attachment["id"])
                    st.rerun()


def _safe_download_name(value):
    name = re.sub(r"[^0-9A-Za-z가-힣._-]+", "_", value.strip())
    return name.strip("._") or "research_note"


def _paragraph(value):
    text = html.escape(value or "").replace("\n", "<br>")
    return text or "<span class=\"empty\">작성된 내용이 없습니다.</span>"


def _embedded_attachments(note_id):
    image_cards = []
    file_items = []

    for attachment in db.get_research_attachments(note_id, with_urls=True):
        name = html.escape(attachment.get("original_name") or "첨부자료")
        url = attachment.get("url")
        kind = attachment.get("attachment_type")
        content_type = attachment.get("content_type") or "application/octet-stream"

        if kind in ("photo", "drawing") and url:
            try:
                request = Request(url, headers={"User-Agent": "IdeaSeedAI/1.0"})
                with urlopen(request, timeout=20) as response:
                    encoded = base64.b64encode(response.read()).decode("ascii")
                image_cards.append(
                    f"<figure><img src='data:{html.escape(content_type)};base64,{encoded}' "
                    f"alt='{name}'><figcaption>{name}</figcaption></figure>"
                )
            except Exception:
                file_items.append(f"<li>{name} (이미지를 불러오지 못했습니다.)</li>")
        else:
            file_items.append(f"<li>{name}</li>")

    parts = []
    if image_cards:
        parts.append("<h2>사진과 그림</h2><div class='gallery'>" + "".join(image_cards) + "</div>")
    if file_items:
        parts.append("<h2>첨부파일 목록</h2><ul>" + "".join(file_items) + "</ul>")
    return "".join(parts)


def build_research_note_html(note, topic):
    ai_section = ""
    if note.get("include_ai"):
        messages = []
        for chat in db.get_chat(int(topic["id"])):
            speaker = "나의 질문" if chat.get("role") == "user" else "AI 연구조교"
            messages.append(
                f"<div class='chat'><strong>{speaker}</strong>"
                f"<p>{_paragraph(chat.get('message'))}</p></div>"
            )
        if messages:
            ai_section = "<h2>AI 질문과 답변</h2>" + "".join(messages)

    sections = [
        ("탐구 질문", note.get("research_question")),
        ("탐구 과정", note.get("process")),
        ("탐구 결과", note.get("result")),
        ("결론과 알게 된 점", note.get("conclusion")),
        ("다음 연구 계획", note.get("next_plan")),
    ]
    body = "".join(
        f"<h2>{title}</h2><div class='content'>{_paragraph(value)}</div>"
        for title, value in sections
    )
    created_at = datetime.now().strftime("%Y-%m-%d")
    attachment_section = _embedded_attachments(note["id"])

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(note.get('title') or '연구노트')}</title>
<style>
body {{ max-width: 820px; margin: 40px auto; padding: 0 24px; color: #24324a;
       font-family: Arial, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif; line-height: 1.7; }}
header {{ padding: 28px; border-radius: 22px; background: #eef9ef; border: 1px solid #d7ecd9; }}
h1 {{ margin: 0 0 8px; color: #237a3b; }}
h2 {{ margin-top: 32px; color: #315caa; font-size: 1.15rem; }}
.content, .chat {{ padding: 18px; border-radius: 14px; background: #f8fafc; }}
.chat {{ margin: 10px 0; }} .chat p {{ margin-bottom: 0; }}
.gallery {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
figure {{ margin: 0; padding: 10px; border: 1px solid #e2e8f0; border-radius: 14px; }}
figure img {{ display: block; width: 100%; height: auto; border-radius: 10px; }}
figcaption {{ margin-top: 8px; color: #667085; font-size: .9rem; word-break: break-all; }}
.empty {{ color: #8a94a6; }} .meta {{ color: #667085; }}
@media print {{ body {{ margin: 0 auto; }} figure {{ break-inside: avoid; }} }}
@media (max-width: 600px) {{ .gallery {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<header>
  <h1>🔬 {html.escape(note.get('title') or '연구노트')}</h1>
  <div class="meta">연구주제: {html.escape(topic.get('name') or '')} · 내려받은 날짜: {created_at}</div>
</header>
{body}
{ai_section}
{attachment_section}
</body>
</html>""".encode("utf-8")


def render_note_download(note, topic):
    section("연구노트 내려받기", "📥")
    st.caption("저장된 최신 연구 내용, AI 대화, 사진과 그림을 문서 하나로 내려받습니다.")
    filename = f"{_safe_download_name(note.get('title') or topic['name'])}.html"
    st.download_button(
        "📥 연구노트 문서 내려받기",
        data=build_research_note_html(note, topic),
        file_name=filename,
        mime="text/html; charset=utf-8",
        use_container_width=True,
        key=f"download_research_note_{note['id']}"
    )
    st.caption("파일을 브라우저에서 연 뒤 인쇄 → PDF로 저장할 수도 있습니다.")


def render_portfolio():
    notes = [
        note for note in db.get_research_notes()
        if bool(note.get("is_portfolio"))
    ]

    st.divider()
    section("나의 연구 포트폴리오", "📁")

    if not notes:
        empty_card(
            "포트폴리오가 비어 있어요.",
            "연구노트에서 '나의 포트폴리오에 추가'를 선택해 보세요.",
            "📁"
        )
        return

    cols = st.columns(2)
    for index, note in enumerate(notes):
        with cols[index % 2]:
            with st.container(border=True):
                st.markdown(f"### {note['fruit']} {note['title']}")
                st.caption(f"연구주제: {note['topic_name']}")
                if note.get("conclusion"):
                    st.write(note["conclusion"])
                status = "🌐 공개" if note.get("is_public") else "🔒 비공개"
                st.caption(status)


def render():
    research_header()
    topics = db.get_topics()

    if not topics:
        empty_card(
            "연구주제가 없습니다.",
            "먼저 성장나무에서 아이디어를 심어보세요.",
            "🌱"
        )
        return

    section("연구주제 선택", "🌳")
    topic_map = {int(topic["id"]): topic for topic in topics}
    selected_id = st.selectbox(
        "연구노트를 작성할 주제",
        options=list(topic_map.keys()),
        format_func=lambda topic_id: (
            f"{topic_map[topic_id]['fruit']} {topic_map[topic_id]['name']}"
        ),
        key="research_topic_select"
    )
    topic = topic_map[selected_id]

    note = render_note_form(topic)

    if note:
        render_note_download(note, topic)
        upload_files(note, selected_id)
        render_saved_attachments(note)
    else:
        st.info("연구노트를 먼저 저장하면 사진, 그림, 파일을 첨부할 수 있습니다.")

    render_portfolio()


# ==========================================================
# END
# ==========================================================
