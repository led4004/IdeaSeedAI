import sqlite3
from pathlib import Path

# =====================================================
# Database Path
# =====================================================

DB_DIR = Path("database")
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "idea_seed_ai.db"


# =====================================================
# Database
# =====================================================

class Database:

    def __init__(self):

        self.conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )

        self.conn.row_factory = sqlite3.Row

        self.create_tables()

    # =================================================
    # Create Tables
    # =================================================

    def create_tables(self):

        cur = self.conn.cursor()

        # ---------------------------------------------
        # 사용자
        # ---------------------------------------------

        cur.execute("""

        CREATE TABLE IF NOT EXISTS profile(

            id INTEGER PRIMARY KEY,

            nickname TEXT,

            level INTEGER DEFAULT 1,

            exp INTEGER DEFAULT 0,

            total_topics INTEGER DEFAULT 0,

            total_failures INTEGER DEFAULT 0,

            total_chats INTEGER DEFAULT 0

        )

        """)

        cur.execute("""

        INSERT OR IGNORE INTO profile(

            id,

            nickname,

            level,

            exp,

            total_topics,

            total_failures,

            total_chats

        )

        VALUES(

            1,

            '새싹 연구원',

            1,

            0,

            0,

            0,

            0

        )

        """)

        # ---------------------------------------------
        # 연구주제
        # ---------------------------------------------

        cur.execute("""

        CREATE TABLE IF NOT EXISTS topics(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE,

            fruit TEXT,

            score INTEGER DEFAULT 0,

            memo TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

        # ---------------------------------------------
        # 실패노트
        # ---------------------------------------------

        cur.execute("""

        CREATE TABLE IF NOT EXISTS failures(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER,

            title TEXT,

            reason TEXT,

            solution TEXT,

            learned TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)

        # ---------------------------------------------
        # AI 대화
        # ---------------------------------------------

        cur.execute("""

        CREATE TABLE IF NOT EXISTS chats(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            topic_id INTEGER,

            role TEXT,

            message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

        """)
        self.create_badge_table()
        self.create_mission_table()

        self.conn.commit()

    # =================================================
    # Profile
    # =================================================

    def get_profile(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM profile

        WHERE id=1

        """)

        return cur.fetchone()

    def add_exp(self, value):

        cur = self.conn.cursor()

        cur.execute("""

        UPDATE profile

        SET exp = exp + ?

        WHERE id=1

        """, (value,))

        self.conn.commit()

        self.level_up()

        self.check_achievements()

    def level_up(self):

        profile = self.get_profile()

        level = profile["level"]

        exp = profile["exp"]

        need = level * 100

        while exp >= need:

            exp -= need

            level += 1

            need = level * 100

        cur = self.conn.cursor()

        cur.execute("""

        UPDATE profile

        SET

        level=?,

        exp=?

        WHERE id=1

        """, (

            level,

            exp

        ))

        self.conn.commit()

    # =================================================
    # Topic
    # =================================================

    def get_topics(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM topics

        ORDER BY id DESC

        """)

        return cur.fetchall()

    def get_topic(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM topics

        WHERE id=?

        """, (

            topic_id,

        ))

        return cur.fetchone()

    def add_topic(
        self,
        name,
        fruit
    ):

        cur = self.conn.cursor()

        cur.execute("""

        INSERT INTO topics(

            name,

            fruit

        )

        VALUES(

            ?,

            ?

        )

        """, (

            name,

            fruit

        ))

        cur.execute("""

        UPDATE profile

        SET total_topics = total_topics + 1

        WHERE id=1

        """)

        self.conn.commit()
        self.add_exp(10)

    def update_topic_score(
        self,
        topic_id,
        score
    ):

        cur = self.conn.cursor()

        cur.execute("""

        UPDATE topics

        SET score=?

        WHERE id=?

        """, (

            score,

            topic_id

        ))

        self.conn.commit()

        if score >= 4:
            self.unlock_badge("발명가")

    def update_topic_memo(
        self,
        topic_id,
        memo
    ):

        cur = self.conn.cursor()

        cur.execute("""

        UPDATE topics

        SET memo=?

        WHERE id=?

        """, (

            memo,

            topic_id

        ))

        self.conn.commit()

    def delete_topic(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("DELETE FROM chats WHERE topic_id=?", (topic_id,))
        cur.execute("DELETE FROM failures WHERE topic_id=?", (topic_id,))
        cur.execute("DELETE FROM topics WHERE id=?", (topic_id,))

        self.conn.commit()


    # =================================================
    # Chat
    # =================================================

    def save_chat(
        self,
        topic_id,
        role,
        message
    ):

        cur = self.conn.cursor()

        cur.execute("""

        INSERT INTO chats(

            topic_id,

            role,

            message

        )

        VALUES(

            ?,

            ?,

            ?

        )

        """, (

            topic_id,

            role,

            message

        ))

        cur.execute("""

        UPDATE profile

        SET total_chats = total_chats + 1

        WHERE id=1

        """)

        self.conn.commit()
        self.add_exp(5)


    def get_chat(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM chats

        WHERE topic_id=?

        ORDER BY id

        """, (

            topic_id,

        ))

        return cur.fetchall()


    def get_last_ai(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM chats

        WHERE topic_id=?

        AND role='assistant'

        ORDER BY id DESC

        LIMIT 1

        """, (

            topic_id,

        ))

        return cur.fetchone()


    def delete_chat(self, chat_id):

        cur = self.conn.cursor()

        cur.execute("""
        UPDATE profile
        SET total_chats=
        CASE
        WHEN total_chats>0
        THEN total_chats-1
        ELSE 0
        END
        WHERE id=1
        """)

        self.conn.commit()


    def clear_chat(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("""

        DELETE FROM chats

        WHERE topic_id=?

        """, (

            topic_id,

        ))

        self.conn.commit()


    # =================================================
    # Failure Note
    # =================================================

    def add_failure(

        self,

        topic_id,

        title,

        reason,

        solution,

        learned

    ):

        cur = self.conn.cursor()

        cur.execute("""

        INSERT INTO failures(

            topic_id,

            title,

            reason,

            solution,

            learned

        )

        VALUES(

            ?,

            ?,

            ?,

            ?,

            ?

        )

        """, (

            topic_id,

            title,

            reason,

            solution,

            learned

        ))

        cur.execute("""

        UPDATE profile

        SET total_failures = total_failures + 1

        WHERE id=1

        """)

        self.conn.commit()
        self.add_exp(20)


    def get_failures(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT

            failures.*,

            topics.name AS topic_name,

            topics.fruit

        FROM failures

        LEFT JOIN topics

        ON failures.topic_id = topics.id

        ORDER BY failures.id DESC

        """)

        return cur.fetchall()


    def get_failures_by_topic(self, topic_id):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM failures

        WHERE topic_id=?

        ORDER BY id DESC

        """, (

            topic_id,

        ))

        return cur.fetchall()

    def delete_failure(self, failure_id):

        cur = self.conn.cursor()

        cur.execute("""
            DELETE FROM failures
            WHERE id=?
        """, (failure_id,))

        cur.execute("""
            UPDATE profile
            SET total_failures=
            CASE
                WHEN total_failures>0
                THEN total_failures-1
                ELSE 0
            END
            WHERE id=1
        """)

        self.conn.commit()


    # =================================================
    # Search
    # =================================================

    def search_topics(self, keyword):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM topics

        WHERE name LIKE ?

        ORDER BY name

        """, (

            f"%{keyword}%",

        ))

        return cur.fetchall()


    def search_failures(self, keyword):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM failures

        WHERE

            title LIKE ?

            OR reason LIKE ?

            OR solution LIKE ?

            OR learned LIKE ?

        ORDER BY id DESC

        """, (

            f"%{keyword}%",

            f"%{keyword}%",

            f"%{keyword}%",

            f"%{keyword}%"

        ))

        return cur.fetchall()


    # =================================================
    # Statistics
    # =================================================

    def total_topics(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT COUNT(*)

        FROM topics

        """)

        return cur.fetchone()[0]


    def total_failures(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT COUNT(*)

        FROM failures

        """)

        return cur.fetchone()[0]


    def total_chats(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT COUNT(*)

        FROM chats

        """)

        return cur.fetchone()[0]


    def finished_topics(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT COUNT(*)

        FROM topics

        WHERE score>=4

        """)

        return cur.fetchone()[0]


    def average_score(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT AVG(score)

        FROM topics

        """)

        value = cur.fetchone()[0]

        if value is None:

            return 0

        return round(value, 2)

    # =================================================
    # Badge
    # =================================================

    def create_badge_table(self):

        cur = self.conn.cursor()

        cur.execute("""

        CREATE TABLE IF NOT EXISTS badges(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE,

            icon TEXT,

            description TEXT,

            unlocked INTEGER DEFAULT 0,

            unlocked_at TIMESTAMP

        )

        """)

        default_badges = [

            ("첫 연구", "🌱", "첫 연구주제를 만들었습니다."),

            ("실험왕", "🧪", "실패노트를 5개 작성했습니다."),

            ("AI 친구", "🤖", "AI와 20번 대화했습니다."),

            ("발명가", "🍎", "연구를 완성했습니다."),

            ("연구마스터", "🏆", "레벨 10 달성")

        ]

        for badge in default_badges:

            cur.execute("""

            INSERT OR IGNORE INTO badges(

                name,

                icon,

                description

            )

            VALUES(

                ?,

                ?,

                ?

            )

            """, badge)

        self.conn.commit()


    def unlock_badge(self, name):

        cur = self.conn.cursor()

        cur.execute("""

        UPDATE badges

        SET unlocked=1,
        unlocked_at=CURRENT_TIMESTAMP

WHERE

name=?

AND unlocked=0

        """, (name,))

        self.conn.commit()


    def get_badges(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM badges

        ORDER BY id

        """)

        return cur.fetchall()


    # =================================================
    # Mission
    # =================================================

    def create_mission_table(self):

        cur = self.conn.cursor()

        cur.execute("""

        CREATE TABLE IF NOT EXISTS missions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            reward INTEGER,

            completed INTEGER DEFAULT 0

        )

        """)

        cur.execute("""

        SELECT COUNT(*)

        FROM missions

        """)

        if cur.fetchone()[0] == 0:

            missions = [

                ("아이디어 하나 만들기",20),

                ("AI와 대화하기",10),

                ("실패노트 작성",30),

                ("스케치하기",20),

                ("연구 완성하기",50)

            ]

            cur.executemany("""

            INSERT INTO missions(

                title,

                reward

            )

            VALUES(

                ?,

                ?

            )

            """, missions)

        self.conn.commit()


    def get_missions(self):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT *

        FROM missions

        """)

        return cur.fetchall()


    def complete_mission(self, mission_id):

        cur = self.conn.cursor()

        cur.execute("""

        SELECT reward

        FROM missions

        WHERE id=?

        """, (mission_id,))

        reward = cur.fetchone()["reward"]

        cur.execute("""

        UPDATE missions

        SET completed=1

        WHERE id=?

        """, (mission_id,))

        self.conn.commit()

        self.add_exp(reward)


    # =================================================
    # Dashboard
    # =================================================

    def dashboard(self):

        return {

            "topics": self.total_topics(),

            "finished": self.finished_topics(),

            "failures": self.total_failures(),

            "chats": self.total_chats(),

            "average": self.average_score(),

            "profile": self.get_profile()

        }


    # =================================================
    # Achievement Check
    # =================================================

    def check_achievements(self):

        profile = self.get_profile()

        if self.total_topics() >= 1:
            self.unlock_badge("첫 연구")

        if self.total_failures() >= 5:
            self.unlock_badge("실험왕")

        if self.total_chats() >= 20:
            self.unlock_badge("AI 친구")

        if self.finished_topics() >= 1:
            self.unlock_badge("발명가")

        if profile["level"] >= 10:
            self.unlock_badge("연구마스터")

db = Database()