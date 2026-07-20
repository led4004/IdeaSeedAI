import streamlit as st

def load_css():
    st.markdown("""
<style>

/* =========================================================
   Idea Seed AI Theme
========================================================= */

:root{

    --green:#67C96B;
    --green2:#7ED957;
    --green3:#B8F28D;

    --bg:#F5FFF6;

    --card:#FFFFFF;

    --text:#2D3748;

    --gray:#94A3B8;

    --yellow:#FFD54F;

    --orange:#FFB84D;

    --red:#FF7A7A;

    --shadow:0 10px 30px rgba(0,0,0,.08);

}

/* ========================================================= */

html,
body,
[data-testid="stAppViewContainer"]{

    background:var(--bg);

    color:var(--text);

}

/* ========================================================= */

.main .block-container{

    max-width:1200px;

    padding-top:18px;

    padding-bottom:50px;

}

/* ========================================================= */

section[data-testid="stSidebar"]{

    background:#ECFAEC;

    border-right:1px solid #DDEEDD;

}

/* ========================================================= */

section[data-testid="stSidebar"] h1,

section[data-testid="stSidebar"] h2,

section[data-testid="stSidebar"] h3{

    color:#2E7D32;

}

/* ========================================================= */

div[data-testid="stMetric"]{

    background:white;

    border-radius:20px;

    padding:18px;

    box-shadow:var(--shadow);

    border:none;

}

/* ========================================================= */

div[data-testid="stMetricLabel"]{

    font-size:15px;

}

div[data-testid="stMetricValue"]{

    font-size:32px;

    font-weight:700;

}

/* ========================================================= */

.stButton>button{

    width:100%;

    border:none;

    border-radius:18px;

    background:linear-gradient(

        135deg,

        var(--green),

        var(--green2)

    );

    color:white;

    padding:14px;

    font-size:17px;

    font-weight:700;

    transition:.25s;

    box-shadow:var(--shadow);

}

/* ========================================================= */

.stButton>button:hover{

    transform:translateY(-3px);

    background:linear-gradient(

        135deg,

        #56C35E,

        #70D66D

    );

}

/* ========================================================= */

.stTextInput input{

    border-radius:18px;

    border:2px solid #D8EFD8;

    background:white;

}

.stTextArea textarea{

    border-radius:18px;

    border:2px solid #D8EFD8;

    background:white;

}

/* ========================================================= */

.stSelectbox div{

    border-radius:16px;

}

/* ========================================================= */

.stProgress>div>div{

    background:linear-gradient(

        90deg,

        var(--green),

        var(--green2)

    );

}

/* ========================================================= */

hr{

    margin-top:18px;

    margin-bottom:18px;

    border:none;

    border-top:1px solid #E5EFE5;

}

/* ========================================================= */

div[data-testid="stChatMessage"]{

    border-radius:22px;

    padding:14px;

    box-shadow:var(--shadow);

    background:white;

    margin-bottom:10px;

}
/* =========================================================
   HEADER
========================================================= */

.header-card{

    background:linear-gradient(
        135deg,
        #7ED957,
        #9BE15D
    );

    border-radius:28px;

    padding:28px;

    box-shadow:var(--shadow);

    color:white;

    margin-bottom:25px;

}

.header-title{

    font-size:34px;

    font-weight:800;

    margin-bottom:6px;

}

.header-sub{

    font-size:16px;

    opacity:.95;

}

.header-level{

    margin-top:18px;

    font-size:22px;

    font-weight:700;

}

.header-exp{

    margin-top:10px;

}

/* =========================================================
   CARD
========================================================= */

.idea-card{

    background:white;

    border-radius:24px;

    padding:22px;

    box-shadow:var(--shadow);

    margin-bottom:18px;

    transition:.25s;

}

.idea-card:hover{

    transform:translateY(-5px);

}

/* =========================================================
   DASHBOARD
========================================================= */

.dashboard-card{

    background:white;

    border-radius:22px;

    padding:18px;

    box-shadow:var(--shadow);

}

/* =========================================================
   TREE
========================================================= */

.tree-card{

    background:white;

    border-radius:30px;

    padding:28px;

    box-shadow:var(--shadow);

    text-align:center;

}

.tree-title{

    font-size:28px;

    font-weight:700;

    color:#2E7D32;

    margin-bottom:15px;

}

.tree-image{

    width:260px;

    margin:auto;

}

.tree-level{

    margin-top:20px;

    font-size:20px;

    font-weight:bold;

}

.tree-exp{

    margin-top:10px;

}

/* =========================================================
   BADGE
========================================================= */

.badge-card{

    background:white;

    border-radius:20px;

    padding:20px;

    box-shadow:var(--shadow);

    text-align:center;

    transition:.2s;

}

.badge-card:hover{

    transform:scale(1.04);

}

.badge-icon{

    font-size:52px;

}

.badge-title{

    margin-top:8px;

    font-weight:bold;

    font-size:20px;

}

.badge-desc{

    margin-top:6px;

    color:#666;

    font-size:14px;

}

/* =========================================================
   MISSION
========================================================= */

.mission-card{

    background:white;

    border-radius:22px;

    padding:18px;

    box-shadow:var(--shadow);

    margin-bottom:15px;

    transition:.2s;

}

.mission-card:hover{

    transform:translateY(-4px);

}

.mission-title{

    font-size:18px;

    font-weight:bold;

}

.mission-reward{

    color:#4CAF50;

    margin-top:5px;

}

/* =========================================================
   EMPTY
========================================================= */

.empty-card{

    background:white;

    border-radius:24px;

    padding:35px;

    text-align:center;

    box-shadow:var(--shadow);

}

.empty-icon{

    font-size:72px;

}

.empty-title{

    margin-top:15px;

    font-size:28px;

    font-weight:bold;

}

.empty-text{

    color:#777;

    margin-top:10px;

}

/* =========================================================
   SUCCESS
========================================================= */

.success-card{

    background:#F3FFF1;

    border-left:8px solid #7ED957;

    border-radius:18px;

    padding:18px;

    margin-bottom:15px;

}

/* =========================================================
   WARNING
========================================================= */

.warning-card{

    background:#FFF9E8;

    border-left:8px solid #FFD54F;

    border-radius:18px;

    padding:18px;

}

/* =========================================================
   ERROR
========================================================= */

.error-card{

    background:#FFF2F2;

    border-left:8px solid #FF6B6B;

    border-radius:18px;

    padding:18px;

}

/* =========================================================
   CHAT
========================================================= */

.chat-user{

    background:#DCFCE7;

    border-radius:22px 22px 6px 22px;

    padding:16px;

    margin:10px 0;

    box-shadow:var(--shadow);

}

.chat-ai{

    background:white;

    border-radius:22px 22px 22px 6px;

    padding:16px;

    margin:10px 0;

    box-shadow:var(--shadow);

}

.chat-name{

    font-size:14px;

    color:#777;

    margin-bottom:8px;

    font-weight:600;

}

/* =========================================================
   FAILURE NOTE
========================================================= */

.failure-card{

    background:white;

    border-radius:24px;

    padding:22px;

    margin-bottom:18px;

    box-shadow:var(--shadow);

    transition:.25s;

}

.failure-card:hover{

    transform:translateY(-4px);

}

.failure-title{

    font-size:22px;

    font-weight:700;

    color:#F44336;

}

.failure-section{

    margin-top:14px;

}

.failure-label{

    font-weight:700;

    color:#444;

}

.failure-content{

    margin-top:5px;

    color:#666;

    line-height:1.7;

}

/* =========================================================
   TOPIC CARD
========================================================= */

.topic-card{

    background:white;

    border-radius:24px;

    padding:22px;

    box-shadow:var(--shadow);

    margin-bottom:18px;

    transition:.25s;

}

.topic-card:hover{

    transform:translateY(-5px);

}

.topic-title{

    font-size:24px;

    font-weight:700;

}

.topic-fruit{

    font-size:34px;

}

.topic-score{

    color:#F9A825;

    font-size:18px;

    margin-top:10px;

}

/* =========================================================
   SKETCH
========================================================= */

.sketch-card{

    background:white;

    border-radius:24px;

    padding:20px;

    box-shadow:var(--shadow);

}

/* =========================================================
   BADGE GRID
========================================================= */

.badge-grid{

    display:flex;

    flex-wrap:wrap;

    gap:18px;

    justify-content:center;

}

.badge-lock{

    filter:grayscale(100%);

    opacity:.45;

}

/* =========================================================
   IMAGE
========================================================= */

img{

    border-radius:18px;

}

/* =========================================================
   SCROLLBAR
========================================================= */

::-webkit-scrollbar{

    width:10px;

}

::-webkit-scrollbar-track{

    background:#EAF8EA;

}

::-webkit-scrollbar-thumb{

    background:#7ED957;

    border-radius:20px;

}

::-webkit-scrollbar-thumb:hover{

    background:#67C96B;

}

/* =========================================================
   ANIMATION
========================================================= */

@keyframes float{

    0%{

        transform:translateY(0);

    }

    50%{

        transform:translateY(-8px);

    }

    100%{

        transform:translateY(0);

    }

}

.float{

    animation:float 3s ease-in-out infinite;

}

@keyframes pop{

    from{

        transform:scale(.8);

        opacity:0;

    }

    to{

        transform:scale(1);

        opacity:1;

    }

}

.pop{

    animation:pop .4s ease;

}

/* =========================================================
   MOBILE
========================================================= */

@media(max-width:768px){

.main .block-container{

padding:15px;

}

.header-title{

font-size:26px;

}

.header-card{

padding:22px;

}

.idea-card{

padding:18px;

}

.tree-image{

width:180px;

}

.topic-title{

font-size:20px;

}

.badge-icon{

font-size:42px;

}

}

/* ========================================================= */

</style>
""", unsafe_allow_html=True)