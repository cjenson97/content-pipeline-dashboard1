import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Content Pipeline · Exec Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Theme Toggle ──────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    st.markdown("### 🎨 Theme")
    dark_mode = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))

st.session_state.theme = "dark" if dark_mode else "light"
theme = st.session_state.theme

# ── Theme Colors ──────────────────────────────────────────────────────────────
if theme == "dark":
    bg = "#0f172a"
    card_bg = "#1e293b"
    border = "#334155"
    text = "#e2e8f0"
    subtext = "#94a3b8"
    table_header = "#1e293b"
else:
    bg = "#ffffff"
    card_bg = "#f8fafc"
    border = "#e2e8f0"
    text = "#0f172a"
    subtext = "#64748b"
    table_header = "#f1f5f9"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>

.stApp {{
    background-color:{bg};
    color:{text};
}}

.metric-card {{
    background:{card_bg};
    border:1px solid {border};
    border-radius:12px;
    padding:16px;
    text-align:center;
}}

.metric-label {{
    font-size:10px;
    font-weight:700;
    color:{subtext};
    text-transform:uppercase;
    letter-spacing:.08em;
}}

.metric-value {{
    font-size:2rem;
    font-weight:900;
    margin:4px 0;
}}

.metric-sub {{
    font-size:11px;
    color:{subtext};
}}

.compare-header {{
    background:#1e293b;
    color:#fff;
    padding:8px 14px;
    border-radius:8px;
    font-size:12px;
    font-weight:700;
    text-align:center;
    margin-bottom:10px;
}}

.summary-box {{
    background:{card_bg};
    border:1px solid {border};
    border-radius:12px;
    padding:16px 20px;
    font-size:13px;
    line-height:1.8;
}}

.up {{color:#10b981;font-weight:700}}
.down {{color:#ef4444;font-weight:700}}
.same {{color:#64748b;font-weight:700}}

</style>
""", unsafe_allow_html=True)

# ── Fetch live API ────────────────────────────────────────────────────────────
API_URL = "http://18.170.93.124:5000/api/stats"

@st.cache_data(ttl=60)
def fetch_stats():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except Exception:
        return None

stats = fetch_stats()

# ── Data ──────────────────────────────────────────────────────────────────────
WEEKS = [
    {"key":"w1","label":"W1  —  18/02 – 22/02","total":120,"success":94,"failed":26,"bot":20,"captcha":2,"pdf":3,"generic":1},
    {"key":"w2","label":"W2  —  23/02 – 01/03","total":165,"success":137,"failed":28,"bot":22,"captcha":2,"pdf":3,"generic":1},
    {"key":"w3","label":"W3  —  02/03 – 08/03","total":165,"success":138,"failed":27,"bot":21,"captcha":2,"pdf":3,"generic":1},
    {"key":"w4","label":"W4  ★  Current  —  09/03 – 15/03","total":195,"success":168,"failed":27,"bot":22,"captcha":2,"pdf":3,"generic":0},
]

ALL_TIME = {
    "key":"all","label":"All Time  —  18/02 – 15/03",
    "total":645,"success":537,"failed":108,
    "bot":85,"captcha":8,"pdf":12,"generic":3
}

ALL_DATA = WEEKS + [ALL_TIME]
OPTIONS = [w["label"] for w in ALL_DATA]

avg_gen_time = 40
if stats and stats.get("avg_gen_time"):
    avg_gen_time = round(float(stats["avg_gen_time"]))

today_total = today_success = today_failed = 0
if stats and stats.get("today"):
    today_total = int(stats["today"].get("total") or 0)
    today_success = int(stats["today"].get("success") or 0)
    today_failed = int(stats["today"].get("failed") or 0)

def get_data(label):
    return next(x for x in ALL_DATA if x["label"] == label)

def success_rate(d): return round(d["success"]/d["total"]*100,1)
def error_rate(d): return round(d["failed"]/d["total"]*100,1)
def bot_pct(d): return round(d["bot"]/d["failed"]*100,1) if d["failed"] else 0
def captcha_pct(d): return round(d["captcha"]/d["failed"]*100,1) if d["failed"] else 0
def pdf_pct(d): return round(d["pdf"]/d["failed"]*100,1) if d["failed"] else 0
def generic_pct(d): return round(d["generic"]/d["failed"]*100,1) if d["failed"] else 0

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Content Pipeline · Executive Dashboard")
st.markdown(f"*Generated {date.today().strftime('%d %B %Y')} · Live data refreshes every 60 seconds*")
st.divider()

mode = st.radio("**View mode**",["Single Period","Compare Two Periods"],horizontal=True)
st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE PERIOD VIEW
# ═══════════════════════════════════════════════════════════════════════════════
if mode == "Single Period":

    selected = st.selectbox("**Period**",OPTIONS,index=3)
    d = get_data(selected)

    sr = success_rate(d)
    er = error_rate(d)
    bp = bot_pct(d)
    cp = captcha_pct(d)
    pp = pdf_pct(d)
    gp = generic_pct(d)

    excl_bot = d["captcha"] + d["pdf"] + d["generic"]
    er_without_bot = round(excl_bot/d["total"]*100,1)
    processing_mins = round(avg_gen_time*d["total"]/60)

    c1,c2,c3,c4,c5 = st.columns(5)

    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Volume</div><div class="metric-value">{d["total"]}</div></div>',unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Success Rate</div><div class="metric-value">{sr}%</div></div>',unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Time</div><div class="metric-value">{avg_gen_time}s</div></div>',unsafe_allow_html=True)

    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Today</div><div class="metric-value">{today_total}</div></div>',unsafe_allow_html=True)

    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Error Rate</div><div class="metric-value">{er}%</div></div>',unsafe_allow_html=True)

    st.divider()

    col_bar,col_donut = st.columns([3,2])

    with col_bar:
        bar = go.Figure(go.Bar(
            x=["No Errors","Bot Protection","CAPTCHA","PDF Timeout","Generic"],
            y=[d["success"],d["bot"],d["captcha"],d["pdf"],d["generic"]],
            marker_color=["#10b981","#ef4444","#8b5cf6","#f59e0b","#6b7280"]
        ))
        bar.update_layout(height=260)
        st.plotly_chart(bar,use_container_width=True)

    with col_donut:
        donut = go.Figure(go.Pie(
            labels=["No Errors","Bot Protection","PDF Timeout","CAPTCHA","Generic"],
            values=[d["success"],d["bot"],d["pdf"],d["captcha"],d["generic"]],
            hole=0.6
        ))
        donut.update_layout(height=260)
        st.plotly_chart(donut,use_container_width=True)

    st.divider()

    st.info(f"⚡ **Pipeline Speed** — {processing_mins} minutes total processing time.")

# ═══════════════════════════════════════════════════════════════════════════════
# COMPARE VIEW
# ═══════════════════════════════════════════════════════════════════════════════
else:

    col1,col2 = st.columns(2)

    with col1:
        sel1 = st.selectbox("Period A",OPTIONS,index=2)
    with col2:
        sel2 = st.selectbox("Period B",OPTIONS,index=3)

    a = get_data(sel1)
    b = get_data(sel2)

    st.markdown("### Comparison")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Period A",
        x=["Success","Bot","CAPTCHA","PDF"],
        y=[a["success"],a["bot"],a["captcha"],a["pdf"]]
    ))

    fig.add_trace(go.Bar(
        name="Period B",
        x=["Success","Bot","CAPTCHA","PDF"],
        y=[b["success"],b["bot"],b["captcha"],b["pdf"]]
    ))

    fig.update_layout(barmode="group",height=350)

    st.plotly_chart(fig,use_container_width=True)

    st.success("Comparison generated.")
