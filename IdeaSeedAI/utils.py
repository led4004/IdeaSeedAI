from datetime import datetime


# ============================================
# 성장 단계
# ============================================

STAGES = {

    0: ("🌱", "씨앗"),

    1: ("🌿", "새싹"),

    2: ("🌳", "나무"),

    3: ("🌸", "꽃"),

    4: ("🍎", "열매")

}


def stage_icon(score):

    return STAGES.get(score, STAGES[0])[0]


def stage_name(score):

    return STAGES.get(score, STAGES[0])[1]


def stage_text(score):

    icon, name = STAGES.get(score, STAGES[0])

    return f"{icon} {name}"


# ============================================
# 진행률
# ============================================

def progress(score):

    return max(0, min(score / 4, 1))


def percent(score):

    return int(progress(score) * 100)


# ============================================
# 점수 색상
# ============================================

def score_color(score):

    if score == 0:
        return "#BDBDBD"

    if score == 1:
        return "#8BC34A"

    if score == 2:
        return "#4CAF50"

    if score == 3:
        return "#FFB300"

    return "#F44336"


# ============================================
# 날짜
# ============================================

def format_date(date_string):

    if not date_string:

        return ""

    try:

        dt = datetime.strptime(

            date_string,

            "%Y-%m-%d %H:%M:%S"

        )

        return dt.strftime("%Y-%m-%d")

    except:

        return date_string


# ============================================
# 문자열
# ============================================

def short_text(text, length=80):

    if text is None:

        return ""

    if len(text) <= length:

        return text

    return text[:length] + "..."


# ============================================
# 레벨
# ============================================

def exp_percent(level, exp):

    need = level * 100

    return exp / need


# ============================================
# 열매
# ============================================

FRUITS = {

    "🍎": "사과",

    "🍓": "딸기",

    "🍇": "포도",

    "🍊": "귤",

    "🍋": "레몬",

    "🥝": "키위",

    "🍉": "수박",

    "🍒": "체리",

    "🥥": "코코넛",

    "🥭": "망고"

}


def fruit_name(icon):

    return FRUITS.get(icon, "")


def fruit_list():

    return list(FRUITS.keys())


# ============================================
# 연구 점수
# ============================================

def average(scores):

    if len(scores) == 0:

        return 0

    return round(

        sum(scores) / len(scores),

        2

    )


# ============================================
# 검색
# ============================================

def contains(text, keyword):

    if text is None:

        return False

    return keyword.lower() in text.lower()


# ============================================
# 아이디어 추천
# ============================================

IDEAS = [

    "AI",

    "환경",

    "드론",

    "로봇",

    "3D프린터",

    "아두이노",

    "라즈베리파이",

    "바다",

    "식물",

    "곤충",

    "우주",

    "자율주행"

]


def random_keywords():

    import random

    return random.sample(

        IDEAS,

        3

    )