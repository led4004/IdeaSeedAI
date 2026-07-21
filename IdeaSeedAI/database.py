import streamlit as st
import mimetypes
import re
import uuid
from pathlib import Path
from datetime import datetime, timezone


BADGES = [
    {"name": "첫 연구", "icon": "🌱", "description": "첫 연구주제를 만들었습니다."},
    {"name": "실험왕", "icon": "🧪", "description": "실패노트를 5개 작성했습니다."},
    {"name": "AI 친구", "icon": "🤖", "description": "AI와 20번 대화했습니다."},
    {"name": "발명가", "icon": "🍎", "description": "연구를 완성했습니다."},
    {"name": "연구마스터", "icon": "🏆", "description": "레벨 10을 달성했습니다."},
]

MISSIONS = [
    {"key": "topic", "title": "아이디어 하나 만들기", "reward": 20},
    {"key": "chat", "title": "AI와 대화하기", "reward": 10},
    {"key": "failure", "title": "실패노트 작성", "reward": 30},
    {"key": "complete", "title": "연구 완성하기", "reward": 50},
]


class Database:
    def _client(self):
        client = st.session_state.get("supabase_client")
        if client is None:
            raise RuntimeError("로그인이 필요합니다.")
        return client

    def _uid(self):
        user = st.session_state.get("auth_user")
        if not user:
            raise RuntimeError("로그인이 필요합니다.")
        return user["id"] if isinstance(user, dict) else user.id

    @staticmethod
    def _one(response):
        return response.data[0] if response.data else None

    def get_profile(self):
        response = self._client().table("profiles").select("*").eq(
            "id", self._uid()
        ).limit(1).execute()
        profile = self._one(response)
        if profile:
            return profile
        email = st.session_state.get("auth_email", "")
        nickname = email.split("@")[0][:20] or "새싹 연구원"
        response = self._client().table("profiles").insert({
            "id": self._uid(), "nickname": nickname
        }).execute()
        return self._one(response)

    def update_nickname(self, nickname):
        nickname = nickname.strip()[:20]
        if len(nickname) < 2:
            return False
        self._client().table("profiles").update({"nickname": nickname}).eq(
            "id", self._uid()
        ).execute()
        return True

    def get_level_info(self):
        profile = self.get_profile()
        level = max(int(profile["level"]), 1)
        exp = max(int(profile["exp"]), 0)
        need = level * 100
        return {"level": level, "exp": exp, "next_level_exp": need,
                "progress": min(exp / need, 1.0)}

    def add_exp(self, value):
        profile = self.get_profile()
        old_level = int(profile["level"])
        level, exp = old_level, int(profile["exp"]) + max(int(value), 0)
        while exp >= level * 100:
            exp -= level * 100
            level += 1
        self._client().table("profiles").update({
            "level": level, "exp": exp
        }).eq("id", self._uid()).execute()
        new_badges = self.check_achievements()
        return {"added_exp": value, "level_up": level > old_level,
                "old_level": old_level, "new_level": level,
                "new_badges": new_badges}

    def _increment_profile(self, field, amount=1):
        profile = self.get_profile()
        self._client().table("profiles").update({
            field: max(int(profile.get(field, 0)) + amount, 0)
        }).eq("id", self._uid()).execute()

    def get_topics(self):
        return self._client().table("topics").select("*").eq(
            "user_id", self._uid()
        ).order("id", desc=True).execute().data

    def get_topic(self, topic_id):
        return self._one(self._client().table("topics").select("*").eq(
            "id", topic_id
        ).eq("user_id", self._uid()).limit(1).execute())

    def add_topic(self, name, fruit):
        name = name.strip()
        exists = self._client().table("topics").select("id").eq(
            "user_id", self._uid()
        ).eq("name", name).limit(1).execute().data
        if exists:
            return False
        response = self._client().table("topics").insert({
            "user_id": self._uid(), "name": name, "fruit": fruit
        }).execute()
        topic = self._one(response)
        if topic:
            self.add_timeline_event(topic["id"], "seed_planted", "연구씨앗을 심었습니다.")
        self._increment_profile("total_topics")
        self.add_exp(10)
        self._auto_complete_mission("topic")
        return True

    def update_topic_score(self, topic_id, score):
        # 성장 단계는 연구 활동을 기준으로 자동 계산합니다.
        return self.refresh_topic_growth(topic_id)["score"]

    def update_topic_memo(self, topic_id, memo):
        self._client().table("topics").update({"memo": memo}).eq(
            "id", topic_id
        ).eq("user_id", self._uid()).execute()
        self.refresh_topic_growth(topic_id)

    def refresh_topic_growth(self, topic_id):
        topic = self.get_topic(topic_id)
        if not topic:
            return {
                "score": 0,
                "memo_done": False,
                "ai_questions": 0,
                "failure_done": False,
                "failure_complete": False
            }

        chats = self._client().table("chats").select("id").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).eq("role", "user").execute().data

        failures = self._client().table("failures").select(
            "reason, solution, learned"
        ).eq("user_id", self._uid()).eq("topic_id", topic_id).execute().data

        memo_done = bool((topic.get("memo") or "").strip())
        ai_questions = len(chats)
        failure_done = len(failures) >= 1
        failure_complete = any(
            bool((failure.get("reason") or "").strip())
            and bool((failure.get("solution") or "").strip())
            and bool((failure.get("learned") or "").strip())
            for failure in failures
        )

        if not memo_done:
            new_score = 0
        elif ai_questions < 2:
            new_score = 1
        elif not failure_done:
            new_score = 2
        elif ai_questions < 4 or not failure_complete:
            new_score = 3
        else:
            new_score = 4

        old_score = int(topic.get("score") or 0)

        if new_score != old_score:
            self._client().table("topics").update({"score": new_score}).eq(
                "id", topic_id
            ).eq("user_id", self._uid()).execute()

        if new_score >= 4 and old_score < 4:
            self.add_exp(30)
            self._auto_complete_mission("complete")
            self.check_achievements()

        return {
            "score": new_score,
            "memo_done": memo_done,
            "ai_questions": ai_questions,
            "failure_done": failure_done,
            "failure_complete": failure_complete
        }

    def delete_topic(self, topic_id):
        topic = self.get_topic(topic_id)
        if not topic:
            return False
        self._client().table("topics").delete().eq("id", topic_id).eq(
            "user_id", self._uid()
        ).execute()
        self._increment_profile("total_topics", -1)
        return True

    def save_chat(self, topic_id, role, message):
        if not self.get_topic(topic_id):
            return False
        self._client().table("chats").insert({
            "user_id": self._uid(), "topic_id": topic_id,
            "role": role, "message": message
        }).execute()
        self._increment_profile("total_chats")
        self.add_exp(5)
        self._auto_complete_mission("chat")
        if role == "user":
            self.add_timeline_event(topic_id, "ai_question", message[:180])
            self.refresh_topic_growth(topic_id)
        return True

    def get_chat(self, topic_id):
        return self._client().table("chats").select("*").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).order("id").execute().data

    def get_last_ai(self, topic_id):
        return self._one(self._client().table("chats").select("*").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).eq("role", "assistant").order(
            "id", desc=True
        ).limit(1).execute())

    def delete_chat(self, chat_id):
        result = self._client().table("chats").delete().eq(
            "id", chat_id
        ).eq("user_id", self._uid()).execute()
        if result.data:
            self._increment_profile("total_chats", -1)

    def clear_chat(self, topic_id):
        rows = self.get_chat(topic_id)
        self._client().table("chats").delete().eq(
            "topic_id", topic_id
        ).eq("user_id", self._uid()).execute()
        self._increment_profile("total_chats", -len(rows))

    def add_failure(self, topic_id, title, reason, solution, learned):
        if not self.get_topic(topic_id):
            return False
        self._client().table("failures").insert({
            "user_id": self._uid(), "topic_id": topic_id, "title": title,
            "reason": reason, "solution": solution, "learned": learned
        }).execute()
        self._increment_profile("total_failures")
        self.add_exp(20)
        self._auto_complete_mission("failure")
        self.refresh_topic_growth(topic_id)
        self.add_timeline_event(topic_id, "failure", f"실패·개선노트: {title}")
        return True

    def get_failures(self):
        failures = self._client().table("failures").select(
            "*, topics(name, fruit)"
        ).eq("user_id", self._uid()).order("id", desc=True).execute().data
        for row in failures:
            topic = row.pop("topics", None) or {}
            row["topic_name"] = topic.get("name", "삭제된 연구")
            row["fruit"] = topic.get("fruit", "🌱")
        return failures

    def get_failures_by_topic(self, topic_id):
        return self._client().table("failures").select("*").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).order("id", desc=True).execute().data

    def delete_failure(self, failure_id):
        result = self._client().table("failures").delete().eq(
            "id", failure_id
        ).eq("user_id", self._uid()).execute()
        if result.data:
            self._increment_profile("total_failures", -1)

    def search_topics(self, keyword):
        return self._client().table("topics").select("*").eq(
            "user_id", self._uid()
        ).ilike("name", f"%{keyword}%").order("name").execute().data

    def search_failures(self, keyword):
        rows = self.get_failures()
        keyword = keyword.lower()
        return [r for r in rows if any(keyword in (r.get(k) or "").lower()
                                       for k in ("title", "reason", "solution", "learned"))]

    def total_topics(self):
        return len(self.get_topics())

    def total_failures(self):
        return len(self.get_failures())

    def total_chats(self):
        return len(self._client().table("chats").select("id").eq(
            "user_id", self._uid()
        ).execute().data)

    def finished_topics(self):
        return len([t for t in self.get_topics() if int(t["score"]) >= 4])

    def average_score(self):
        topics = self.get_topics()
        return round(sum(int(t["score"]) for t in topics) / len(topics), 2) if topics else 0

    def unlock_badge(self, name):
        exists = self._client().table("user_badges").select("id").eq(
            "user_id", self._uid()
        ).eq("badge_name", name).limit(1).execute().data
        if exists:
            return False
        self._client().table("user_badges").insert({
            "user_id": self._uid(), "badge_name": name
        }).execute()
        return True

    def get_badges(self):
        owned = {r["badge_name"]: r for r in self._client().table(
            "user_badges"
        ).select("*").eq("user_id", self._uid()).execute().data}
        return [{**badge, "unlocked": int(badge["name"] in owned),
                 "unlocked_at": owned.get(badge["name"], {}).get("unlocked_at")}
                for badge in BADGES]

    def get_unlocked_badges(self):
        return [b for b in self.get_badges() if b["unlocked"]]

    def get_locked_badges(self):
        return [b for b in self.get_badges() if not b["unlocked"]]

    def check_achievements(self):
        checks = {"첫 연구": self.total_topics() >= 1,
                  "실험왕": self.total_failures() >= 5,
                  "AI 친구": self.total_chats() >= 20,
                  "발명가": self.finished_topics() >= 1,
                  "연구마스터": int(self.get_profile()["level"]) >= 10}
        return [name for name, ok in checks.items() if ok and self.unlock_badge(name)]

    def get_missions(self):
        completed = {r["mission_key"] for r in self._client().table(
            "user_missions"
        ).select("mission_key").eq("user_id", self._uid()).execute().data}
        return [{"id": i + 1, **m, "completed": int(m["key"] in completed)}
                for i, m in enumerate(MISSIONS)]

    def _auto_complete_mission(self, key):
        mission = next((m for m in MISSIONS if m["key"] == key), None)
        if not mission:
            return None
        exists = self._client().table("user_missions").select("id").eq(
            "user_id", self._uid()
        ).eq("mission_key", key).limit(1).execute().data
        if exists:
            return None
        self._client().table("user_missions").insert({
            "user_id": self._uid(), "mission_key": key
        }).execute()
        return self.add_exp(mission["reward"])

    def complete_mission(self, mission_id):
        if not 1 <= int(mission_id) <= len(MISSIONS):
            return None
        return self._auto_complete_mission(MISSIONS[int(mission_id) - 1]["key"])

    def dashboard(self):
        return {"topics": self.total_topics(), "finished": self.finished_topics(),
                "failures": self.total_failures(), "chats": self.total_chats(),
                "average": self.average_score(), "profile": self.get_profile(),
                "level_info": self.get_level_info(), "badges": self.get_badges()}

    # =================================================
    # Research Notes
    # =================================================

    def get_research_note(self, topic_id):
        return self._one(self._client().table("research_notes").select("*").eq(
            "topic_id", topic_id
        ).eq("user_id", self._uid()).limit(1).execute())

    def get_research_notes(self):
        rows = self._client().table("research_notes").select(
            "*, topics(name, fruit, score)"
        ).eq("user_id", self._uid()).order("updated_at", desc=True).execute().data
        for row in rows:
            topic = row.pop("topics", None) or {}
            row["topic_name"] = topic.get("name", "삭제된 연구")
            row["fruit"] = topic.get("fruit", "🌱")
            row["score"] = topic.get("score", 0)
        return rows

    def save_research_note(self, topic_id, data):
        if not self.get_topic(topic_id):
            return None
        payload = {
            "user_id": self._uid(),
            "topic_id": topic_id,
            "title": (data.get("title") or "연구노트").strip()[:120],
            "research_question": (data.get("research_question") or "").strip(),
            "process": (data.get("process") or "").strip(),
            "result": (data.get("result") or "").strip(),
            "conclusion": (data.get("conclusion") or "").strip(),
            "next_plan": (data.get("next_plan") or "").strip(),
            "include_ai": bool(data.get("include_ai", True)),
            "is_public": bool(data.get("is_public", False)),
            "is_portfolio": bool(data.get("is_portfolio", False)),
            "updated_at": "now()"
        }
        existing = self.get_research_note(topic_id)
        if existing:
            payload.pop("user_id", None)
            payload.pop("topic_id", None)
            payload.pop("updated_at", None)
            response = self._client().table("research_notes").update(payload).eq(
                "id", existing["id"]
            ).eq("user_id", self._uid()).execute()
        else:
            payload.pop("updated_at", None)
            response = self._client().table("research_notes").insert(payload).execute()
        saved = self._one(response)
        self.add_timeline_event(
            topic_id,
            "note_updated" if existing else "note_created",
            "연구노트를 수정했습니다." if existing else "연구노트를 만들었습니다."
        )
        return saved

    # =================================================
    # Idea Seeds / Timeline / Evaluation
    # =================================================

    def add_idea_seed(self, idea, category="생활", attachment_name="",
                      attachment_bytes=None, content_type=""):
        idea = (idea or "").strip()[:100]
        if not idea:
            return None
        storage_path = ""
        if attachment_name and attachment_bytes:
            safe_name = self._safe_filename(attachment_name)
            storage_path = f"{self._uid()}/{uuid.uuid4().hex}_{safe_name}"
            self._client().storage.from_("seed-files").upload(
                storage_path, attachment_bytes,
                {"content-type": content_type or "application/octet-stream", "upsert": "false"}
            )
        response = self._client().table("idea_seeds").insert({
            "user_id": self._uid(), "idea": idea,
            "category": category, "attachment_name": attachment_name or "",
            "storage_path": storage_path, "content_type": content_type or ""
        }).execute()
        return self._one(response)

    def get_idea_seeds(self, status="all", keyword="", oldest=False):
        query = self._client().table("idea_seeds").select("*").eq(
            "user_id", self._uid()
        )
        if status != "all":
            query = query.eq("status", status)
        if keyword.strip():
            query = query.ilike("idea", f"%{keyword.strip()}%")
        rows = query.order("created_at", desc=not oldest).execute().data
        for row in rows:
            row["attachment_url"] = None
            if row.get("storage_path"):
                try:
                    signed = self._client().storage.from_("seed-files").create_signed_url(
                        row["storage_path"], 3600
                    )
                    row["attachment_url"] = signed.get("signedURL") or signed.get("signedUrl")
                except Exception:
                    pass
        return rows

    def update_idea_seed(self, seed_id, idea, category, favorite=False):
        self._client().table("idea_seeds").update({
            "idea": idea.strip()[:100], "category": category,
            "is_favorite": bool(favorite)
        }).eq("id", seed_id).eq("user_id", self._uid()).execute()

    def delete_idea_seed(self, seed_id):
        seed = self._one(self._client().table("idea_seeds").select("*").eq(
            "id", seed_id
        ).eq("user_id", self._uid()).limit(1).execute())
        if seed and seed.get("storage_path"):
            self._client().storage.from_("seed-files").remove([seed["storage_path"]])
        self._client().table("idea_seeds").delete().eq(
            "id", seed_id
        ).eq("user_id", self._uid()).execute()

    def plant_idea_seed(self, seed_id, fruit, reason, problem, first_solution):
        seed = self._one(self._client().table("idea_seeds").select("*").eq(
            "id", seed_id
        ).eq("user_id", self._uid()).limit(1).execute())
        if not seed or seed.get("status") == "research":
            return None
        if not self.add_topic(seed["idea"], fruit):
            return None
        topic = self._one(self._client().table("topics").select("*").eq(
            "user_id", self._uid()
        ).eq("name", seed["idea"]).limit(1).execute())
        memo = "\n".join([
            f"탐구 이유: {reason.strip()}", f"해결 문제: {problem.strip()}",
            f"첫 해결방법: {first_solution.strip()}"
        ])
        self.update_topic_memo(topic["id"], memo)
        self._client().table("idea_seeds").update({
            "status": "research", "topic_id": topic["id"],
            "planted_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", seed_id).eq("user_id", self._uid()).execute()
        self.add_timeline_event(topic["id"], "seed_detail", "탐구 이유와 해결 방법을 정리했습니다.")
        return topic

    def add_timeline_event(self, topic_id, event_type, content, attachment_name=""):
        try:
            self._client().table("research_timeline").insert({
                "user_id": self._uid(), "topic_id": topic_id,
                "event_type": event_type, "content": (content or "")[:1000],
                "attachment_name": attachment_name or ""
            }).execute()
            return True
        except Exception:
            return False

    def get_timeline(self, topic_id):
        return self._client().table("research_timeline").select("*").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).order("created_at").execute().data

    def save_evaluation(self, topic_id, data):
        payload = {
            "user_id": self._uid(), "topic_id": topic_id,
            "similar_ideas": data.get("similar_ideas", ""),
            "patent_reference": data.get("patent_reference", ""),
            "technology": data.get("technology", ""),
            "strengths": data.get("strengths", ""),
            "weaknesses": data.get("weaknesses", ""),
            "feasibility": int(data.get("feasibility", 3)),
            "creativity": int(data.get("creativity", 3)),
            "improvement": data.get("improvement", ""),
            "ai_summary": data.get("ai_summary", ""),
            "total_score": int(data.get("total_score", 60))
        }
        response = self._client().table("idea_evaluations").upsert(
            payload, on_conflict="user_id,topic_id"
        ).execute()
        self.add_timeline_event(topic_id, "evaluation", f"아이디어 발전 평가: {payload['total_score']}점")
        return self._one(response)

    def get_evaluation(self, topic_id):
        return self._one(self._client().table("idea_evaluations").select("*").eq(
            "user_id", self._uid()
        ).eq("topic_id", topic_id).limit(1).execute())

    def delete_research_note(self, note_id):
        attachments = self.get_research_attachments(note_id)
        for attachment in attachments:
            try:
                self._client().storage.from_("research-files").remove([
                    attachment["storage_path"]
                ])
            except Exception:
                pass
        self._client().table("research_notes").delete().eq(
            "id", note_id
        ).eq("user_id", self._uid()).execute()

    @staticmethod
    def _safe_filename(filename):
        name = Path(filename or "file").name
        name = re.sub(r"[^A-Za-z0-9가-힣._-]", "_", name)
        return name[:100] or "file"

    def upload_research_attachment(self, note_id, topic_id, filename, content,
                                   content_type=None, attachment_type="file"):
        note = self.get_research_note(topic_id)
        if not note or int(note["id"]) != int(note_id):
            return None
        safe_name = self._safe_filename(filename)
        storage_path = f"{self._uid()}/{topic_id}/{uuid.uuid4().hex}_{safe_name}"
        mime = content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        self._client().storage.from_("research-files").upload(
            storage_path,
            content,
            {"content-type": mime, "upsert": "false"}
        )
        response = self._client().table("research_attachments").insert({
            "note_id": note_id,
            "user_id": self._uid(),
            "storage_path": storage_path,
            "original_name": safe_name,
            "content_type": mime,
            "attachment_type": attachment_type
        }).execute()
        return self._one(response)

    def get_research_attachments(self, note_id, with_urls=False):
        rows = self._client().table("research_attachments").select("*").eq(
            "note_id", note_id
        ).order("created_at").execute().data
        if with_urls:
            for row in rows:
                try:
                    signed = self._client().storage.from_(
                        "research-files"
                    ).create_signed_url(row["storage_path"], 3600)
                    row["url"] = (
                        signed.get("signedURL")
                        or signed.get("signedUrl")
                        or signed.get("signed_url")
                    )
                except Exception:
                    row["url"] = None
        return rows

    def delete_research_attachment(self, attachment_id):
        row = self._one(self._client().table("research_attachments").select("*").eq(
            "id", attachment_id
        ).eq("user_id", self._uid()).limit(1).execute())
        if not row:
            return False
        self._client().storage.from_("research-files").remove([row["storage_path"]])
        self._client().table("research_attachments").delete().eq(
            "id", attachment_id
        ).eq("user_id", self._uid()).execute()
        return True

    def publish_topic(self, topic_id):
        topic = self.get_topic(topic_id)
        if not topic or int(topic["score"]) < 4:
            return False
        existing = self._client().table("market_posts").select("id").eq(
            "topic_id", topic_id
        ).eq("user_id", self._uid()).limit(1).execute().data
        payload = {"user_id": self._uid(), "topic_id": topic_id,
                   "title": topic["name"], "fruit": topic["fruit"],
                   "description": topic.get("memo") or "멋진 연구 열매가 완성됐어요!"}
        if existing:
            self._client().table("market_posts").update(payload).eq(
                "id", existing[0]["id"]
            ).execute()
        else:
            self._client().table("market_posts").insert(payload).execute()
        return True

    def unpublish_topic(self, topic_id):
        self._client().table("market_posts").delete().eq(
            "topic_id", topic_id
        ).eq("user_id", self._uid()).execute()

    def is_topic_published(self, topic_id):
        return bool(self._client().table("market_posts").select("id").eq(
            "topic_id", topic_id
        ).eq("user_id", self._uid()).limit(1).execute().data)

    def get_market_posts(self, sort="latest", keyword=""):
        query = self._client().table("market_feed").select("*")
        if keyword.strip():
            query = query.ilike("title", f"%{keyword.strip()}%")
        order = "like_count" if sort == "popular" else "created_at"
        return query.order(order, desc=True).execute().data

    def get_market_post_details(self, post_id):
        post = self._one(self._client().table("market_posts").select("*").eq(
            "id", post_id
        ).limit(1).execute())

        if not post:
            return {"topic": None, "failures": [], "chats": []}

        topic_id = post["topic_id"]
        topic = self._one(self._client().table("topics").select("*").eq(
            "id", topic_id
        ).limit(1).execute())
        failures = self._client().table("failures").select("*").eq(
            "topic_id", topic_id
        ).order("created_at").execute().data
        chats = self._client().table("chats").select("*").eq(
            "topic_id", topic_id
        ).order("created_at").execute().data

        research_note = self._one(self._client().table("research_notes").select("*").eq(
            "topic_id", topic_id
        ).eq("is_public", True).limit(1).execute())
        research_attachments = []
        if research_note:
            research_attachments = self.get_research_attachments(
                research_note["id"], with_urls=True
            )

        return {
            "topic": topic,
            "failures": failures,
            "chats": chats,
            "research_note": research_note,
            "research_attachments": research_attachments
        }

    def toggle_like(self, post_id):
        query = self._client().table("market_likes").select("id").eq(
            "post_id", post_id
        ).eq("user_id", self._uid()).limit(1).execute()
        if query.data:
            self._client().table("market_likes").delete().eq(
                "id", query.data[0]["id"]
            ).execute()
            return False
        self._client().table("market_likes").insert({
            "post_id": post_id, "user_id": self._uid()
        }).execute()
        return True

    def has_liked(self, post_id):
        return bool(self._client().table("market_likes").select("id").eq(
            "post_id", post_id
        ).eq("user_id", self._uid()).limit(1).execute().data)

    def add_market_comment(self, post_id, content, comment_type="cheer"):
        content = content.strip()[:500]
        if not content or comment_type not in ("cheer", "idea"):
            return False
        self._client().table("market_comments").insert({
            "post_id": post_id, "user_id": self._uid(),
            "content": content, "comment_type": comment_type
        }).execute()
        return True

    def get_market_comments(self, post_id):
        return self._client().table("market_comments_view").select("*").eq(
            "post_id", post_id
        ).order("created_at").execute().data

    def delete_market_comment(self, comment_id):
        self._client().table("market_comments").delete().eq(
            "id", comment_id
        ).eq("user_id", self._uid()).execute()


db = Database()
