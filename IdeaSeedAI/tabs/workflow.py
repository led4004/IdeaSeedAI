import html
import json
import re
from datetime import datetime

import streamlit as st

from components import section, empty_card
from database import db


FRUITS = ["🍎 사과", "🍊 귤", "🍋 레몬", "🍇 포도", "🍑 복숭아"]
CATEGORIES = ["생활", "과학", "발명", "SW", "환경", "로봇"]
EVENT_ICONS = {
    "seed_planted": "🌱", "seed_detail": "🎯", "ai_question": "🤖",
    "note_created": "📝", "note_updated": "✏️", "activity": "🔬",
    "evaluation": "🔍", "failure": "💥"
}


def _extract_json(text):
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I)
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    if not match:
        raise ValueError("AI 평가 형식을 읽지 못했습니다.")
    return json.loads(match.group(0))


def _go(page):
    st.session_state.page = page
    st.rerun()


def seed_vault():
    st.markdown('<div class="header-card"><h1>🌰 씨앗보관함</h1><p>떠오른 생각을 모으고 탐구할 씨앗을 골라보세요.</p></div>', unsafe_allow_html=True)
    section("새 생각씨앗 기록", "💡")
    with st.form("quick_seed", clear_on_submit=True):
        idea = st.text_input("한 줄 생각", max_chars=100, placeholder="예: 자동으로 물을 주는 화분")
        category = st.selectbox("분류", CATEGORIES)
        attachment = st.file_uploader("사진 또는 기록 파일(선택)", type=["png", "jpg", "jpeg", "webp", "txt", "pdf"])
        save = st.form_submit_button("🌰 씨앗보관함에 저장", use_container_width=True)
    if save:
        if not idea.strip():
            st.warning("생각을 한 줄 이상 입력해주세요.")
        else:
            db.add_idea_seed(
                idea, category, attachment.name if attachment else "",
                attachment.getvalue() if attachment else None,
                attachment.type if attachment else ""
            )
            st.success("생각씨앗을 저장했습니다!")
            st.rerun()

    section("저장한 씨앗", "🗃️")
    c1, c2, c3 = st.columns([2, 1, 1])
    keyword = c1.text_input("검색", placeholder="씨앗 검색", label_visibility="collapsed")
    status = c2.selectbox("상태", ["all", "idea", "research"], format_func=lambda x: {"all":"전체", "idea":"생각씨앗", "research":"연구씨앗"}[x], label_visibility="collapsed")
    oldest = c3.selectbox("정렬", [False, True], format_func=lambda x: "오래된순" if x else "최신순", label_visibility="collapsed")
    seeds = db.get_idea_seeds(status, keyword, oldest)
    if not seeds:
        empty_card("저장된 씨앗이 없어요.", "첫 생각씨앗을 기록해 보세요.", "🌰")
        return

    for seed in seeds:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                star = "⭐ " if seed.get("is_favorite") else ""
                st.markdown(f"### {star}{html.escape(seed['idea'])}")
                state = "🌱 연구씨앗" if seed["status"] == "research" else "🌰 생각씨앗"
                st.caption(f"{state} · {seed['category']} · {str(seed['created_at'])[:10]}")
                if seed.get("attachment_name"):
                    st.caption(f"📎 {seed['attachment_name']}")
                if seed.get("attachment_url"):
                    if (seed.get("content_type") or "").startswith("image/"):
                        st.image(seed["attachment_url"], width=240)
                    else:
                        st.link_button("첨부자료 열기", seed["attachment_url"])
            with right:
                if seed["status"] == "idea" and st.button("🌱 이 씨앗 심기", key=f"plant_{seed['id']}", use_container_width=True):
                    st.session_state.plant_seed_id = seed["id"]
                    st.rerun()
                if st.button("🗑️ 삭제", key=f"seed_delete_{seed['id']}", use_container_width=True):
                    db.delete_idea_seed(seed["id"])
                    st.rerun()

        if st.session_state.get("plant_seed_id") == seed["id"]:
            with st.form(f"plant_form_{seed['id']}"):
                st.markdown("#### 🌱 연구씨앗으로 구체화하기")
                reason = st.text_area("왜 탐구하고 싶나요?", max_chars=200)
                problem = st.text_area("해결하고 싶은 문제", max_chars=200)
                solution = st.text_area("처음 생각한 해결 방법", max_chars=200)
                fruit = st.selectbox("성장나무 열매", FRUITS)
                planted = st.form_submit_button("씨앗 심기 시작하기 🌱", use_container_width=True)
            if planted:
                if not problem.strip() or not solution.strip():
                    st.warning("해결 문제와 첫 해결방법을 입력하세요.")
                else:
                    topic = db.plant_idea_seed(seed["id"], fruit.split()[0], reason, problem, solution)
                    if topic:
                        st.session_state.pop("plant_seed_id", None)
                        st.session_state.page = "mentor"
                        st.success("연구씨앗을 심었습니다!")
                        st.rerun()
                    else:
                        st.error("이미 같은 이름의 연구가 있거나 씨앗을 심을 수 없습니다.")


def timeline():
    st.markdown('<div class="header-card"><h1>📅 탐구로그</h1><p>아이디어가 자라는 과정을 시간순으로 확인하세요.</p></div>', unsafe_allow_html=True)
    topics = db.get_topics()
    if not topics:
        empty_card("연구주제가 없어요.", "씨앗보관함에서 씨앗을 먼저 심어보세요.", "🌱")
        return
    topic_map = {int(t["id"]): t for t in topics}
    topic_id = st.selectbox("연구주제", list(topic_map), format_func=lambda i: f"{topic_map[i]['fruit']} {topic_map[i]['name']}")
    with st.form("manual_timeline", clear_on_submit=True):
        content = st.text_area("새 활동 기록", placeholder="자료조사, 실험, 제작, 관찰 내용을 적어보세요.")
        attachment = st.file_uploader("자료 이름 기록(선택)")
        added = st.form_submit_button("➕ 탐구 활동 추가", use_container_width=True)
    if added and content.strip():
        db.add_timeline_event(topic_id, "activity", content, attachment.name if attachment else "")
        st.rerun()

    events = db.get_timeline(topic_id)
    chats = len([c for c in db.get_chat(topic_id) if c["role"] == "user"])
    m1, m2, m3 = st.columns(3)
    m1.metric("탐구 기록", f"{len(events)}개")
    m2.metric("AI 질문", f"{chats}개")
    m3.metric("수정·개선", f"{len([e for e in events if e['event_type'] in ('note_updated','failure')])}회")
    if not events:
        st.info("아직 탐구로그가 없습니다.")
    for event in events:
        icon = EVENT_ICONS.get(event["event_type"], "📌")
        with st.container(border=True):
            st.markdown(f"**{icon} {event['content']}**")
            st.caption(str(event["created_at"]).replace("T", " ")[:16])
            if event.get("attachment_name"):
                st.caption(f"📎 {event['attachment_name']}")
    if st.button("🔍 이 아이디어 평가하기", use_container_width=True):
        _go("evaluation")


def evaluation():
    st.markdown('<div class="header-card"><h1>🔍 AI 아이디어 발전센터</h1><p>아이디어의 가능성과 새로운 점을 살펴봅니다.</p></div>', unsafe_allow_html=True)
    topics = db.get_topics()
    if not topics:
        empty_card("평가할 연구가 없어요.", "먼저 연구씨앗을 심어주세요.", "🌱")
        return
    topic_map = {int(t["id"]): t for t in topics}
    topic_id = st.selectbox("평가할 연구", list(topic_map), format_func=lambda i: f"{topic_map[i]['fruit']} {topic_map[i]['name']}")
    topic = topic_map[topic_id]
    note = db.get_research_note(topic_id) or {}
    old = db.get_evaluation(topic_id) or {}
    st.info("특허·기술 평가는 법률 판단이 아니라 탐구를 위한 참고자료입니다.")
    if st.button("🤖 AI 평가 초안 만들기", use_container_width=True):
        try:
            from .mentor import ask_ai, has_api_key
            if not has_api_key():
                st.warning("AI 연구조교의 API 키 설정을 먼저 확인하세요.")
            else:
                prompt = f"""다음 학생 아이디어를 교육용으로 평가해줘.
아이디어: {topic['name']}
초기 내용: {topic.get('memo') or ''}
연구노트: {note.get('process') or ''} {note.get('result') or ''} {note.get('conclusion') or ''}
반드시 아래 JSON만 출력해. 초등·중학생이 이해할 쉬운 한국어를 사용해.
실제 검색을 하지 않았으므로 특허 등록 여부를 단정하지 마.
{{
  "similar_ideas": "비슷한 제품이나 방법과 공통점·차이점",
  "patent_reference": "특허 검색 때 확인할 핵심어와 주의점",
  "technology": "필요한 과학 원리와 기술",
  "feasibility": 1부터 5까지 정수,
  "creativity": 1부터 5까지 정수,
  "strengths": "좋은 점 2~3개",
  "weaknesses": "부족한 점 2~3개",
  "improvement": "기능·구조·재료·사용법 개선안 3개",
  "ai_summary": "전체 평가를 두세 문장으로 요약"
}}"""
                with st.spinner("AI가 아이디어를 살펴보고 있어요..."):
                    raw = ask_ai(topic["name"], prompt, [])
                    st.session_state[f"ai_eval_{topic_id}"] = _extract_json(raw)
                st.rerun()
        except Exception as error:
            st.error(f"AI 평가 초안을 만들지 못했습니다: {error}")
    ai_draft = st.session_state.get(f"ai_eval_{topic_id}", {})
    if ai_draft:
        with st.expander("🤖 AI 평가 초안", expanded=True):
            st.success(ai_draft.get("ai_summary", "AI 평가 초안이 완성되었습니다."))
    with st.form(f"evaluation_{topic_id}"):
        similar = st.text_area("① 유사 아이디어 분석", value=old.get("similar_ideas") or ai_draft.get("similar_ideas", ""), placeholder="비슷한 제품이나 방법")
        patent = st.text_area("② 특허·기술 검색 참고", value=old.get("patent_reference") or ai_draft.get("patent_reference", ""), help="법률 판단이 아닌 탐구용 검색어와 참고 정보입니다.")
        technology = st.text_area("③ 필요한 과학 원리와 기술", value=old.get("technology") or ai_draft.get("technology", ""))
        c1, c2 = st.columns(2)
        feasibility = c1.slider("④ 기술 구현 가능성", 1, 5, int(old.get("feasibility") or ai_draft.get("feasibility", 3)))
        creativity = c2.slider("⑤ 창의성·차별성", 1, 5, int(old.get("creativity") or ai_draft.get("creativity", 3)))
        strengths = st.text_area("⑥ 좋은 점", value=old.get("strengths") or ai_draft.get("strengths", ""))
        weaknesses = st.text_area("⑦ 부족한 점", value=old.get("weaknesses") or ai_draft.get("weaknesses", ""))
        improvement = st.text_area("⑧ AI 개선 제안", value=old.get("improvement") or ai_draft.get("improvement", ""), placeholder="기능·구조·재료·사용법 개선")
        summary = st.text_area("⑨ 종합 평가", value=old.get("ai_summary") or ai_draft.get("ai_summary", ""))
        saved = st.form_submit_button("📊 평가 저장", use_container_width=True)
    if saved:
        score = (feasibility + creativity) * 10
        db.save_evaluation(topic_id, {
            "similar_ideas": similar, "patent_reference": patent,
            "technology": technology, "strengths": strengths,
            "weaknesses": weaknesses, "feasibility": feasibility,
            "creativity": creativity, "improvement": improvement,
            "ai_summary": summary, "total_score": score
        })
        st.success(f"평가를 저장했습니다. 종합 점수는 {score}점입니다.")
        st.rerun()
    if old:
        st.metric("종합 평가", f"{old['total_score']}점")
    c1, c2 = st.columns(2)
    if c1.button("💥 개선노트 작성", use_container_width=True):
        _go("failure")
    if c2.button("📁 포트폴리오 보기", use_container_width=True):
        _go("portfolio")


def _portfolio_html(topic, note, events, evaluation, failures):
    def p(value):
        return html.escape(str(value or "")).replace("\n", "<br>")
    timeline_items = "".join(f"<li><b>{p(str(e['created_at'])[:10])}</b> {p(e['content'])}</li>" for e in events)
    failure_items = "".join(f"<li><b>{p(f['title'])}</b> — {p(f.get('learned'))}</li>" for f in failures)
    return f"""<!doctype html><html lang='ko'><meta charset='utf-8'><title>{p(topic['name'])}</title>
<style>body{{max-width:850px;margin:40px auto;font-family:Arial,sans-serif;line-height:1.7;color:#24324a;padding:20px}}header{{background:#eef9ef;padding:28px;border-radius:20px}}h1{{color:#237a3b}}h2{{color:#315caa;margin-top:30px}}section{{background:#f8fafc;padding:18px;border-radius:14px;margin:12px 0}}</style>
<header><h1>{p(topic['fruit'])} {p(topic['name'])}</h1><p>IdeaSeedAI 연구 포트폴리오 · {datetime.now().strftime('%Y-%m-%d')}</p></header>
<h2>최초 아이디어</h2><section>{p(topic.get('memo'))}</section>
<h2>연구노트</h2><section><b>{p(note.get('title'))}</b><p>{p(note.get('research_question'))}</p><p>{p(note.get('process'))}</p><p>{p(note.get('result'))}</p><p>{p(note.get('conclusion'))}</p></section>
<h2>탐구로그</h2><ol>{timeline_items or '<li>기록 없음</li>'}</ol>
<h2>발전 평가</h2><section>종합 {p(evaluation.get('total_score'))}점<br>{p(evaluation.get('improvement'))}</section>
<h2>실패와 개선</h2><ul>{failure_items or '<li>기록 없음</li>'}</ul></html>""".encode("utf-8")


def portfolio():
    st.markdown('<div class="header-card"><h1>📁 연구 포트폴리오</h1><p>씨앗부터 열매까지의 연구 과정을 한 문서로 정리합니다.</p></div>', unsafe_allow_html=True)
    topics = db.get_topics()
    if not topics:
        empty_card("포트폴리오가 비어 있어요.", "연구주제를 먼저 만들어보세요.", "📁")
        return
    for topic in topics:
        with st.container(border=True):
            st.markdown(f"### {topic['fruit']} {topic['name']}")
            stage = ["생각씨앗", "연구씨앗", "새싹", "꽃", "열매"][min(int(topic.get('score') or 0), 4)]
            st.caption(f"현재 단계: {stage} · 성장도 {int(topic.get('score') or 0) * 25}%")
            note = db.get_research_note(topic["id"]) or {}
            events = db.get_timeline(topic["id"])
            evaluation_data = db.get_evaluation(topic["id"]) or {}
            failures = db.get_failures_by_topic(topic["id"])
            data = _portfolio_html(topic, note, events, evaluation_data, failures)
            st.download_button("📄 포트폴리오 내려받기", data=data, file_name=f"{topic['name']}_포트폴리오.html", mime="text/html", key=f"portfolio_{topic['id']}", use_container_width=True)


def render(page):
    if page == "seeds":
        seed_vault()
    elif page == "timeline":
        timeline()
    elif page == "evaluation":
        evaluation()
    elif page == "portfolio":
        portfolio()


# END
