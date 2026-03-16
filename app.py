import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Content Pipeline - Exec Dashboard", page_icon="📊", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

spacer, toggle_col = st.columns([11, 1])
with toggle_col:
    st.session_state.dark_mode = st.toggle("🌙", value=st.session_state.dark_mode, help="Toggle dark mode")

dm = st.session_state.dark_mode

if dm:
    BG             = "#0f1117"
    SURFACE        = "#1a1d27"
    SURFACE2       = "#21252f"
    BORDER         = "#2d3142"
    TEXT_PRI       = "#d4d8e8"
    TEXT_SEC       = "#7b82a0"
    TEXT_MUTED     = "#4e5470"
    PLOT_BG        = "rgba(0,0,0,0)"
    GRID_COLOR     = "#1e2233"
    GREEN          = "#3dba8c"
    RED            = "#c95f5f"
    AMBER          = "#c9913a"
    PURPLE         = "#7c6fbf"
    GREY           = "#5a5f72"
    INDIGO         = "#6b71c4"
    SUMMARY_BG     = "#131a24"
    SUMMARY_BOR    = "#1e3048"
    UP_COL         = "#3dba8c"
    DOWN_COL       = "#c95f5f"
    SAME_COL       = "#5a5f72"
    TABLE_HEAD     = "#1a1d27"
    TABLE_HEAD_TXT = "#7b82a0"
    TABLE_SUC      = "#111f19"
    TABLE_ERR      = "#1f1318"
    TABLE_PUR      = "#18152a"
    TABLE_AMB      = "#1e1910"
    TABLE_BASE     = "#161920"
    COMPARE_HDR    = "#1a1d27"
    COMPARE_TXT    = "#d4d8e8"
else:
    BG             = "#ffffff"
    SURFACE        = "#f8fafc"
    SURFACE2       = "#f1f5f9"
    BORDER         = "#e2e8f0"
    TEXT_PRI       = "#0f172a"
    TEXT_SEC       = "#64748b"
    TEXT_MUTED     = "#94a3b8"
    PLOT_BG        = "rgba(0,0,0,0)"
    GRID_COLOR     = "#f1f5f9"
    GREEN          = "#10b981"
    RED            = "#ef4444"
    AMBER          = "#f59e0b"
    PURPLE         = "#8b5cf6"
    GREY           = "#6b7280"
    INDIGO         = "#6366f1"
    SUMMARY_BG     = "#f0f9ff"
    SUMMARY_BOR    = "#bae6fd"
    UP_COL         = "#10b981"
    DOWN_COL       = "#ef4444"
    SAME_COL       = "#64748b"
    TABLE_HEAD     = "#f1f5f9"
    TABLE_HEAD_TXT = "#64748b"
    TABLE_SUC      = "#f0fdf4"
    TABLE_ERR      = "#fef2f2"
    TABLE_PUR      = "#faf5ff"
    TABLE_AMB      = "#fffbeb"
    TABLE_BASE     = "#f8fafc"
    COMPARE_HDR    = "#1e293b"
    COMPARE_TXT    = "#ffffff"

css = (
    "<style>"
    ".stApp, .stApp > div, section[data-testid='stMain'] > div, div[data-testid='stAppViewContainer'] {"
    "background-color: " + BG + " !important; color: " + TEXT_PRI + " !important;}"
    "section[data-testid='stSidebar'] {background-color: " + SURFACE + " !important;}"
    ".stMarkdown, .stMarkdown p, .stMarkdown li, label, .stRadio label,"
    "div[data-testid='stMarkdownContainer'] p {color: " + TEXT_PRI + " !important;}"
    "hr {border-color: " + BORDER + " !important;}"
    "div[data-baseweb='select'] > div {background-color: " + SURFACE + " !important; border-color: " + BORDER + " !important; color: " + TEXT_PRI + " !important;}"
    "div[data-baseweb='select'] span {color: " + TEXT_PRI + " !important;}"
    "div[data-baseweb='menu'] {background-color: " + SURFACE + " !important;}"
    "div[data-baseweb='menu'] li {color: " + TEXT_PRI + " !important; background-color: " + SURFACE + " !important;}"
    "div[data-baseweb='menu'] li:hover {background-color: " + SURFACE2 + " !important;}"
    "div[data-baseweb='radio'] label {color: " + TEXT_PRI + " !important;}"
    "div[data-testid='stAlert'] {background-color: " + SURFACE + " !important; border-color: " + BORDER + " !important; color: " + TEXT_PRI + " !important;}"
    ".metric-card {background: " + SURFACE + "; border: 1px solid " + BORDER + "; border-radius: 12px; padding: 16px; text-align: center;}"
    ".metric-label {font-size: 10px; font-weight: 700; color: " + TEXT_SEC + "; text-transform: uppercase; letter-spacing: .08em;}"
    ".metric-value {font-size: 2rem; font-weight: 900; margin: 4px 0;}"
    ".metric-sub {font-size: 11px; color: " + TEXT_MUTED + ";}"
    ".compare-header {background: " + COMPARE_HDR + "; color: " + COMPARE_TXT + "; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 700; text-align: center; margin-bottom: 10px;}"
    ".summary-box {background: " + SUMMARY_BG + "; border: 1px solid " + SUMMARY_BOR + "; border-radius: 12px; padding: 16px 20px; font-size: 13px; line-height: 1.8; color: " + TEXT_PRI + ";}"
    ".up {color: " + UP_COL + "; font-weight: 700;}"
    ".down {color: " + DOWN_COL + "; font-weight: 700;}"
    ".same {color: " + SAME_COL + "; font-weight: 700;}"
    "table {color: " + TEXT_PRI + " !important;}"
    "td, th {color: " + TEXT_PRI + " !important;}"
    "div[data-testid='stToggle'] label {color: " + TEXT_SEC + " !important;}"
    "</style>"
)
st.markdown(css, unsafe_allow_html=True)

DASHBOARD_BASE = "http://18.170.93.124:5000"
API_URL = DASHBOARD_BASE + "/api/stats"


def get_daily_cache_key():
    now = datetime.now()
    if now.hour >= 16:
        return now.strftime("%Y-%m-%d")
    return (now - timedelta(days=1)).strftime("%Y-%m-%d")


@st.cache_data(ttl=60)
def fetch_stats():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=86400)
def fetch_failing_sources(_cache_key):
    all_failed = []
    offset = 0
    while True:
        try:
            r = requests.get(
                DASHBOARD_BASE + "/generated-list-more",
                params={"filter": "all", "vertical": "all", "offset": offset},
                timeout=15
            )
            html = r.text
        except Exception:
            break
        parts = html.split('class="article-item')
        parts.pop(0)
        if not parts:
            break
        for div in parts:
            em = re.search(r'text-red-500[^>]*>\s*\n?\s*([\w\s]+)\n?\s*</p', div)
            if not em:
                continue
            etype = em.group(1).strip()
            if etype not in ("Bot blocked", "Processing error", "Timed out", "No content"):
                continue
            im = re.search(r'hx-get="/article/(\d+)/([a-f0-9]{32})"', div)
            if im:
                all_failed.append({"id": im.group(1), "guid": im.group(2)})
        if "Load more" not in html:
            break
        offset += 100
        if offset >= 700:
            break

    def fetch_domain(art):
        try:
            detail = requests.get(DASHBOARD_BASE + "/article/" + art["id"] + "/" + art["guid"], timeout=10).text
            um = re.search(r'href="(https?://[^"]+)"', detail)
            if not um:
                return None
            return urlparse(um.group(1)).netloc.lstrip("www.")
        except Exception:
            return None

    domain_counts = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_domain, art): art for art in all_failed}
        for future in as_completed(futures):
            d = future.result()
            if d:
                domain_counts[d] = domain_counts.get(d, 0) + 1
    return sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)


stats = fetch_stats()
cache_key = get_daily_cache_key()

HISTORIC_WEEKS = [
    {"key": "w1", "label": "W1 - 18/02 - 22/02", "total": 120, "success": 94,  "failed": 26, "bot": 20, "captcha": 2, "pdf": 3, "generic": 1},
    {"key": "w2", "label": "W2 - 23/02 - 01/03", "total": 165, "success": 137, "failed": 28, "bot": 22, "captcha": 2, "pdf": 3, "generic": 1},
    {"key": "w3", "label": "W3 - 02/03 - 08/03", "total": 165, "success": 138, "failed": 27, "bot": 21, "captcha": 2, "pdf": 3, "generic": 1},
    {"key": "w4", "label": "W4 - 09/03 - 15/03", "total": 195, "success": 168, "failed": 27, "bot": 22, "captcha": 2, "pdf": 3, "generic": 0},
]

WEEK_SCHEDULE = {
    8:  {"key": "w1", "start": date(2026, 2, 18), "end": date(2026, 2, 22), "short": "W1"},
    9:  {"key": "w2", "start": date(2026, 2, 23), "end": date(2026, 3,  1), "short": "W2"},
    10: {"key": "w3", "start": date(2026, 3,  2), "end": date(2026, 3,  8), "short": "W3"},
    11: {"key": "w4", "start": date(2026, 3,  9), "end": date(2026, 3, 15), "short": "W4"},
    12: {"key": "w5", "start": date(2026, 3, 16), "end": date(2026, 3, 22), "short": "W5"},
    13: {"key": "w6", "start": date(2026, 3, 23), "end": date(2026, 3, 29), "short": "W6"},
    14: {"key": "w7", "start": date(2026, 3, 30), "end": date(2026, 4,  5), "short": "W7"},
    15: {"key": "w8", "start": date(2026, 4,  6), "end": date(2026, 4, 12), "short": "W8"},
}


def build_weeks(stats_data):
    now = datetime.now()
    current_iso = now.isocalendar()[1]
    live_total = 0
    live_success = 0
    live_failed = 0
    if stats_data and stats_data.get("week"):
        live_total   = int(stats_data["week"].get("total")   or 0)
        live_success = int(stats_data["week"].get("success") or 0)
        live_failed  = int(stats_data["week"].get("failed")  or 0)
    live_bot     = round(live_failed * 0.79)
    live_captcha = round(live_failed * 0.07)
    live_pdf     = round(live_failed * 0.11)
    live_generic = max(live_failed - live_bot - live_captcha - live_pdf, 0)
    sched = WEEK_SCHEDULE.get(current_iso)
    if sched:
        cur_label = sched["short"] + " Current - " + sched["start"].strftime("%d/%m") + " - " + sched["end"].strftime("%d/%m")
        cur_key = sched["key"]
    else:
        cur_label = "Current Week W" + str(current_iso)
        cur_key = "w" + str(current_iso)
    current_entry = {
        "key": cur_key, "label": cur_label,
        "total": live_total, "success": live_success, "failed": live_failed,
        "bot": live_bot, "captcha": live_captcha, "pdf": live_pdf, "generic": live_generic,
    }
    past_isos = sorted(iso for iso in WEEK_SCHEDULE if iso < current_iso)
    weeks = []
    for iso in past_isos:
        frozen = next((w for w in HISTORIC_WEEKS if w["key"] == WEEK_SCHEDULE[iso]["key"]), None)
        if frozen:
            weeks.append(frozen)
    weeks.append(current_entry)
    return weeks, current_entry


WEEKS, CURRENT_WEEK = build_weeks(stats)

ALL_TIME = {
    "key": "all",
    "label": "All Time - 18/02 - " + date.today().strftime("%d/%m"),
    "total":   sum(w["total"]   for w in WEEKS),
    "success": sum(w["success"] for w in WEEKS),
    "failed":  sum(w["failed"]  for w in WEEKS),
    "bot":     sum(w["bot"]     for w in WEEKS),
    "captcha": sum(w["captcha"] for w in WEEKS),
    "pdf":     sum(w["pdf"]     for w in WEEKS),
    "generic": sum(w["generic"] for w in WEEKS),
}

ALL_DATA = WEEKS + [ALL_TIME]
OPTIONS  = [w["label"] for w in ALL_DATA]

avg_gen_time  = 40
today_total   = 0
today_success = 0
today_failed  = 0
if stats:
    if stats.get("avg_gen_time"):
        avg_gen_time = round(float(stats["avg_gen_time"]))
    if stats.get("today"):
        today_total   = int(stats["today"].get("total")   or 0)
        today_success = int(stats["today"].get("success") or 0)
        today_failed  = int(stats["today"].get("failed")  or 0)


def get_data(label):
    return next(x for x in ALL_DATA if x["label"] == label)

def success_rate(d): return round(d["success"] / d["total"] * 100, 1) if d["total"] > 0 else 0
def error_rate(d):   return round(d["failed"]  / d["total"] * 100, 1) if d["total"] > 0 else 0
def bot_pct(d):      return round(d["bot"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def captcha_pct(d):  return round(d["captcha"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def pdf_pct(d):      return round(d["pdf"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def generic_pct(d):  return round(d["generic"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0

def base_layout(height=250, title=None):
    layout = dict(
        height=height,
        margin=dict(t=30 if title else 10, b=10, l=0, r=0),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG, showlegend=False,
        yaxis=dict(gridcolor=GRID_COLOR, color=TEXT_SEC, zerolinecolor=BORDER),
        xaxis=dict(gridcolor=GRID_COLOR, color=TEXT_SEC),
        font=dict(color=TEXT_SEC),
    )
    if title:
        layout["title"] = dict(text=title, font=dict(color=TEXT_PRI, size=13))
    return layout

C_SUCCESS = GREEN
C_BOT     = RED
C_CAPTCHA = PURPLE
C_PDF     = AMBER
C_GENERIC = GREY

st.markdown("## Content Pipeline - Executive Dashboard")
st.markdown("*Generated " + date.today().strftime("%d %B %Y") + " - Live data refreshes every 60 seconds*")
st.divider()

mode = st.radio("**View mode**", ["Single Period", "Compare Two Periods"], horizontal=True)
st.divider()

# =============================================================================
# SINGLE PERIOD
# =============================================================================
if mode == "Single Period":

    selected = st.selectbox("**Period**", OPTIONS, index=len(OPTIONS) - 2)
    d = get_data(selected)

    sr = success_rate(d)
    er = error_rate(d)
    bp = bot_pct(d)
    cp = captcha_pct(d)
    pp = pdf_pct(d)
    gp = generic_pct(d)
    excl_bot        = d["captcha"] + d["pdf"] + d["generic"]
    er_without_bot  = round(excl_bot / d["total"] * 100, 1) if d["total"] > 0 else 0
    processing_mins = round(avg_gen_time * d["total"] / 60)
    period_label    = "this week" if d["key"] != "all" else "all time"

    c1, c2, c3, c4, c5 = st.columns(5)
    vol_label = "Weekly Volume" if d["key"] != "all" else "Total Volume"
    vol_sub   = "articles this week" if d["key"] != "all" else "articles all time"

    card_vol  = '<div class="metric-card" style="border-left:4px solid ' + INDIGO + '"><div class="metric-label">' + vol_label + '</div><div class="metric-value" style="color:' + INDIGO + '">' + str(d["total"]) + '</div><div class="metric-sub">' + vol_sub + '</div></div>'
    card_sr   = '<div class="metric-card" style="border-left:4px solid ' + GREEN  + '"><div class="metric-label">Success Rate</div><div class="metric-value" style="color:' + GREEN  + '">' + str(sr) + '%</div><div class="metric-sub">' + str(d["success"]) + ' of ' + str(d["total"]) + ' articles</div></div>'
    card_spd  = '<div class="metric-card" style="border-left:4px solid ' + AMBER  + '"><div class="metric-label">Avg Gen Time</div><div class="metric-value" style="color:' + AMBER  + '">' + str(avg_gen_time) + 's</div><div class="metric-sub">per article (live)</div></div>'
    tc        = TEXT_MUTED if today_total == 0 else AMBER
    ts        = "no articles yet today" if today_total == 0 else str(today_success) + " success - " + str(today_failed) + " failed"
    card_tod  = '<div class="metric-card" style="border-left:4px solid ' + AMBER  + '"><div class="metric-label">Today\'s Output</div><div class="metric-value" style="color:' + tc + '">' + str(today_total) + '</div><div class="metric-sub">' + ts + '</div></div>'
    card_er   = '<div class="metric-card" style="border-left:4px solid ' + RED    + '"><div class="metric-label">Error Rate</div><div class="metric-value" style="color:' + RED    + '">' + str(er) + '%</div><div class="metric-sub">' + str(d["failed"]) + ' of ' + str(d["total"]) + ' failed</div></div>'

    with c1: st.markdown(card_vol,  unsafe_allow_html=True)
    with c2: st.markdown(card_sr,   unsafe_allow_html=True)
    with c3: st.markdown(card_spd,  unsafe_allow_html=True)
    with c4: st.markdown(card_tod,  unsafe_allow_html=True)
    with c5: st.markdown(card_er,   unsafe_allow_html=True)

    st.divider()

    col_bar, col_donut = st.columns([3, 2])
    with col_bar:
        st.markdown("**Volume by Outcome - " + d["label"] + "**")
        bar = go.Figure(go.Bar(
            x=["No Errors", "Bot Protection", "CAPTCHA", "PDF Timeout", "Generic"],
            y=[d["success"], d["bot"], d["captcha"], d["pdf"], d["generic"]],
            marker_color=[C_SUCCESS, C_BOT, C_CAPTCHA, C_PDF, C_GENERIC]
        ))
        bar.update_layout(**base_layout(250))
        st.plotly_chart(bar, use_container_width=True)

    with col_donut:
        st.markdown("**Distribution**")
        donut = go.Figure(go.Pie(
            labels=["No Errors", "Bot Protection", "PDF Timeout", "CAPTCHA", "Generic"],
            values=[d["success"], d["bot"], d["pdf"], d["captcha"], d["generic"]],
            hole=0.6,
            marker_colors=[C_SUCCESS, C_BOT, C_PDF, C_CAPTCHA, C_GENERIC]
        ))
        donut.update_layout(
            margin=dict(t=10, b=10, l=0, r=0), height=250,
            paper_bgcolor=PLOT_BG,
            legend=dict(font=dict(size=10, color=TEXT_SEC)),
            font=dict(color=TEXT_SEC),
        )
        st.plotly_chart(donut, use_container_width=True)

    st.divider()

    st.markdown("**Error Trends - Weekly Since Monitoring Start (18 Feb 2026)**")
    wl = [w["label"].split("-")[0].strip() for w in WEEKS]
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(name="Bot Protection",   x=wl, y=[w["bot"]     for w in WEEKS], mode="lines+markers", line=dict(color=C_BOT,     width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="PDF Timeout",      x=wl, y=[w["pdf"]     for w in WEEKS], mode="lines+markers", line=dict(color=C_PDF,     width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="CAPTCHA",          x=wl, y=[w["captcha"] for w in WEEKS], mode="lines+markers", line=dict(color=C_CAPTCHA, width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="Generic Fallback", x=wl, y=[w["generic"] for w in WEEKS], mode="lines+markers", line=dict(color=C_GENERIC, width=2, dash="dash"), marker=dict(size=8)))
    fig_line.update_layout(
        height=280, margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        yaxis=dict(gridcolor=GRID_COLOR, title="Error count", color=TEXT_SEC, zerolinecolor=BORDER),
        xaxis=dict(gridcolor=GRID_COLOR, color=TEXT_SEC),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11, color=TEXT_SEC)),
        font=dict(color=TEXT_SEC),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    st.markdown("**Error Type Detail - " + d["label"] + "**")
    suc_share = str(round(d["success"] / d["total"] * 100, 1)) + "%" if d["total"] > 0 else "0%"

    tbl = '<table style="width:100%;border-collapse:collapse;font-size:13px;">'
    tbl += '<thead><tr style="background:' + TABLE_HEAD + ';font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;">'
    tbl += '<th style="padding:10px 14px;text-align:left;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Error Type</th>'
    tbl += '<th style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Count</th>'
    tbl += '<th style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Share</th>'
    tbl += '<th style="padding:10px 14px;text-align:left;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Description and Action</th>'
    tbl += '</tr></thead><tbody>'
    tbl += '<tr style="background:' + TABLE_SUC + '"><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + GREEN  + ';font-weight:600;">No Errors</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_PRI + ';font-weight:700;">' + str(d["success"]) + '</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">' + suc_share + '</td><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">Article successfully fetched, processed and published. No action required.</td></tr>'
    tbl += '<tr style="background:' + TABLE_ERR + '"><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + RED    + ';font-weight:600;">Bot Protection / Access Blocked</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_PRI + ';font-weight:700;">' + str(d["bot"])     + '</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">' + str(bp) + '%</td><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">Website blocked automated access. Analyst must open source manually and write update.</td></tr>'
    tbl += '<tr style="background:' + TABLE_PUR + '"><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + PURPLE + ';font-weight:600;">CAPTCHA / Security Check</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_PRI + ';font-weight:700;">' + str(d["captcha"]) + '</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">' + str(cp) + '%</td><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">Page requires a security check. Analyst should review source and write update manually.</td></tr>'
    tbl += '<tr style="background:' + TABLE_AMB + '"><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + AMBER  + ';font-weight:600;">PDF Timeout</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_PRI + ';font-weight:700;">' + str(d["pdf"])     + '</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">' + str(pp) + '%</td><td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + TEXT_SEC + ';">PDF took too long to load. Analyst should review document directly and write update manually.</td></tr>'
    tbl += '<tr style="background:' + TABLE_BASE + '"><td style="padding:10px 14px;color:' + TEXT_SEC + ';font-weight:600;">Generic Fallback</td><td style="padding:10px 14px;text-align:right;color:' + TEXT_PRI + ';font-weight:700;">' + str(d["generic"])  + '</td><td style="padding:10px 14px;text-align:right;color:' + TEXT_SEC + ';">' + str(gp) + '%</td><td style="padding:10px 14px;color:' + TEXT_SEC + ';">Source could not be accessed automatically. Analyst to review source manually.</td></tr>'
    tbl += '</tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)

    st.divider()

    now      = datetime.now()
    next_run = now.replace(hour=16, minute=0, second=0, microsecond=0)
    if now.hour >= 16:
        next_run = next_run + timedelta(days=1)
    secs_until = int((next_run - now).total_seconds())
    hrs_until  = secs_until // 3600
    mins_until = (secs_until % 3600) // 60
    if hrs_until > 0:
        next_label = str(hrs_until) + "h " + str(mins_until) + "m"
    else:
        next_label = str(mins_until) + "m"
    last_run = "today at 16:00" if now.hour >= 16 else "yesterday at 16:00"

    st.markdown(
        "**Top 5 Failing Sources** "
        "<span style='font-size:11px;color:" + TEXT_MUTED + ";'>"
        "Updated daily at 16:00 - last updated " + last_run + " - next update in " + next_label + "</span>",
        unsafe_allow_html=True
    )

    with st.spinner("Loading source data..."):
        failing_sources = fetch_failing_sources(cache_key)

    top5 = failing_sources[:5]

    if top5:
        max_count   = top5[0][1]
        rank_colors = [RED, AMBER, AMBER, TEXT_SEC, TEXT_SEC]
        row_bgs     = [TABLE_ERR, TABLE_AMB, TABLE_AMB, TABLE_BASE, TABLE_BASE]

        t5 = '<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        t5 += '<thead><tr style="background:' + TABLE_HEAD + ';font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;">'
        t5 += '<th style="padding:10px 14px;text-align:left;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Rank</th>'
        t5 += '<th style="padding:10px 14px;text-align:left;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Source Domain</th>'
        t5 += '<th style="padding:10px 14px;text-align:right;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Failures</th>'
        t5 += '<th style="padding:10px 14px;text-align:left;border-bottom:1px solid ' + BORDER + ';color:' + TABLE_HEAD_TXT + ';">Relative Volume</th>'
        t5 += '</tr></thead><tbody>'

        for i, (domain, count) in enumerate(top5):
            bar_pct = round(count / max_count * 100)
            col     = rank_colors[i]
            row_bg  = row_bgs[i]
            t5 += '<tr style="background:' + row_bg + '">'
            t5 += '<td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';color:' + col + ';font-weight:700;font-size:15px;">#' + str(i + 1) + '</td>'
            t5 += '<td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';font-weight:600;color:' + TEXT_PRI + ';font-family:monospace;font-size:12px;">' + domain + '</td>'
            t5 += '<td style="padding:10px 14px;border-bottom:1px solid ' + BORDER + ';text-align:right;font-weight:700;color:' + col + ';">' + str(count) + '</td>'
            t5 += '<td style="padding:10px 28px 10px 14px;border-bottom:1px solid ' + BORDER + ';width:35%;"><div style="background:' + BORDER + ';border-radius:4px;height:8px;overflow:hidden;"><div style="background:' + col + ';width:' + str(bar_pct) + '%;height:8px;border-radius:4px;"></div></div></td>'
            t5 += '</tr>'

        t5 += '</tbody></table>'
        st.markdown(t5, unsafe_allow_html=True)

        total_failures = sum(c for _, c in failing_sources)
        unique_sources = len(failing_sources)
        st.markdown(
            '<p style="font-size:11px;color:' + TEXT_MUTED + ';margin-top:8px;">' +
            str(total_failures) + ' total failed articles across ' + str(unique_sources) + ' unique sources</p>',
            unsafe_allow_html=True
        )
    else:
        st.info("No failing source data available.")

    st.divider()

    f1, f2, f3 = st.columns(3)
    with f1:
        st.info("Pipeline Speed\n\nAverage " + str(avg_gen_time) + " seconds per article. At " + str(d["total"]) + " articles that is approximately **" + str(processing_mins) + " minutes** of total processing time.")
    with f2:
        st.error("Top Error Driver\n\nBot Protection accounts for " + str(bp) + "% of all failures. Fixing this would reduce error rate from " + str(er) + "% to approximately **" + str(er_without_bot) + "%**.")
    with f3:
        st.success("Weekly Throughput\n\n**" + str(d["total"]) + " articles** " + period_label + ". " + str(d["failed"]) + " articles required manual analyst intervention.")

# =============================================================================
# COMPARE VIEW
# =============================================================================
else:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel1 = st.selectbox("**Period A**", OPTIONS, index=len(OPTIONS) - 3)
    with col_sel2:
        sel2 = st.selectbox("**Period B**", OPTIONS, index=len(OPTIONS) - 2)

    a = get_data(sel1)
    b = get_data(sel2)

    sr_a, sr_b = success_rate(a), success_rate(b)
    er_a, er_b = error_rate(a),   error_rate(b)

    st.divider()

   h1, h2 = st.columns(2)
    with h1:
        st.markdown('<div class="compare-header">A  ' + a["label"] + '</div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="compare-header">B  ' + b["label"] + '</div>', unsafe_allow_html=True)

    def kpi_card(label, val_a, val_b, unit="", higher_is_better=True, color_a=None, color_b=None):
        color_a = color_a or INDIGO
        color_b = color_b or INDIGO
        diff = round(val_b - val_a, 1)
        if diff > 0:
            arrow_sym  = "up" if higher_is_better else "down"
            diff_color = UP_COL if higher_is_better else DOWN_COL
            arr        = "▲"
        elif diff < 0:
            arrow_sym  = "down" if higher_is_better else "up"
            diff_color = DOWN_COL if higher_is_better else UP_COL
            arr        = "▼"
        else:
            arrow_sym, diff_color, arr = "same", SAME_COL, "→"
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<div class="metric-card" style="border-left:4px solid ' + color_a + '">'
                '<div class="metric-label">' + label + '</div>'
                '<div class="metric-value" style="color:' + color_a + '">' + str(val_a) + unit + '</div>'
                '</div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                '<div class="metric-card" style="border-left:4px solid ' + color_b + '">'
                '<div class="metric-value" style="color:' + color_b + '">' + str(val_b) + unit + '</div>'
                '<div class="metric-sub" style="color:' + diff_color + ';font-weight:700;">' + arr + ' ' + str(abs(diff)) + unit + ' vs Period A</div>'
                '</div>',
                unsafe_allow_html=True
            )

    kpi_card("Total Articles",  a["total"],   b["total"],   higher_is_better=True,  color_a=INDIGO, color_b=INDIGO)
    kpi_card("Success Rate",    sr_a,         sr_b,         unit="%", higher_is_better=True,  color_a=GREEN,  color_b=GREEN)
    kpi_card("Error Rate",      er_a,         er_b,         unit="%", higher_is_better=False, color_a=RED,    color_b=RED)
    kpi_card("Failed Articles", a["failed"],  b["failed"],  higher_is_better=False, color_a=RED,    color_b=RED)
    kpi_card("Bot Errors",      a["bot"],     b["bot"],     higher_is_better=False, color_a=RED,    color_b=RED)
    kpi_card("PDF Timeouts",    a["pdf"],     b["pdf"],     higher_is_better=False, color_a=AMBER,  color_b=AMBER)
    kpi_card("CAPTCHA Errors",  a["captcha"], b["captcha"], higher_is_better=False, color_a=PURPLE, color_b=PURPLE)

    st.divider()

    ch1, ch2 = st.columns(2)
    for col, d_chart, lbl in [(ch1, a, "A"), (ch2, b, "B")]:
        with col:
            fig = go.Figure(go.Bar(
                x=["No Errors", "Bot", "CAPTCHA", "PDF", "Generic"],
                y=[d_chart["success"], d_chart["bot"], d_chart["captcha"], d_chart["pdf"], d_chart["generic"]],
                marker_color=[C_SUCCESS, C_BOT, C_CAPTCHA, C_PDF, C_GENERIC]
            ))
            fig.update_layout(**base_layout(220, title="Period " + lbl + " - " + d_chart["label"]))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("### Comparison Summary")

    def trend(val_a, val_b, higher_is_better=True):
        if val_b > val_a:
            return ("improved", "up") if higher_is_better else ("worsened", "down")
        elif val_b < val_a:
            return ("declined", "down") if higher_is_better else ("improved", "up")
        return ("unchanged", "same")

    def fmt_diff(val, cls):
        sign = "+" if val > 0 else ""
        return '<span class="' + cls + '">' + sign + str(val) + '</span>'

    vol_trend, vol_cls = trend(a["total"],   b["total"])
    sr_trend,  sr_cls  = trend(sr_a,         sr_b)
    er_trend,  er_cls  = trend(er_a,         er_b,         higher_is_better=False)
    bot_trend, bot_cls = trend(a["bot"],     b["bot"],     higher_is_better=False)
    pdf_trend, pdf_cls = trend(a["pdf"],     b["pdf"],     higher_is_better=False)
    cap_trend, cap_cls = trend(a["captcha"], b["captcha"], higher_is_better=False)

    vol_diff = b["total"]   - a["total"]
    sr_diff  = round(sr_b   - sr_a, 1)
    er_diff  = round(er_b   - er_a, 1)
    bot_diff = b["bot"]     - a["bot"]
    pdf_diff = b["pdf"]     - a["pdf"]
    cap_diff = b["captcha"] - a["captcha"]

    if sr_cls == "up":
        sr_note = "a positive trend showing pipeline reliability is increasing."
    elif sr_cls == "down":
        sr_note = "success rate fell, worth investigating the cause."
    else:
        sr_note = "no change in pipeline reliability."

    if b["bot"] > b["pdf"] and b["bot"] > b["captcha"]:
        bot_note = "this remains the top error driver and the primary focus for remediation."
    else:
        bot_note = "bot protection is no longer the top error driver."

    if er_cls == "down":
        footer_note = "Watch: Error rate increased period-on-period. Review source access patterns."
    elif sr_cls == "up":
        footer_note = "Positive: Overall pipeline performance improved between these two periods."
    else:
        footer_note = "Performance was broadly stable between these two periods."

    summary = (
        '<div class="summary-box">'
        "<strong>Period A:</strong> " + a["label"] + " &nbsp;|&nbsp; <strong>Period B:</strong> " + b["label"] + "<br><br>"
        "Volume: Article output " + vol_trend + " from <strong>" + str(a["total"]) + "</strong> to <strong>" + str(b["total"]) + "</strong> (" + fmt_diff(vol_diff, vol_cls) + " articles).<br><br>"
        "Success Rate: " + sr_trend.capitalize() + " from <strong>" + str(sr_a) + "%</strong> to <strong>" + str(sr_b) + "%</strong> (" + fmt_diff(sr_diff, sr_cls) + "pp) - " + sr_note + "<br><br>"
        "Error Rate: " + er_trend.capitalize() + " from <strong>" + str(er_a) + "%</strong> to <strong>" + str(er_b) + "%</strong> (" + fmt_diff(er_diff, er_cls) + "pp).<br><br>"
        "Bot Protection errors " + bot_trend + " from <strong>" + str(a["bot"]) + "</strong> to <strong>" + str(b["bot"]) + "</strong> (" + fmt_diff(bot_diff, bot_cls) + ") - " + bot_note + "<br><br>"
        "PDF Timeouts " + pdf_trend + " (" + fmt_diff(pdf_diff, pdf_cls) + ") &nbsp;·&nbsp; "
        "CAPTCHA errors " + cap_trend + " (" + fmt_diff(cap_diff, cap_cls) + ").<br><br>"
        + footer_note +
        "</div>"
    )

    st.markdown(summary, unsafe_allow_html=True)
