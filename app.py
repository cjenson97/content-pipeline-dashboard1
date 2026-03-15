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

# ── Dark mode state ───────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Theme CSS injection ───────────────────────────────────────────────────────
dark = st.session_state.dark_mode

if dark:
    bg_main       = "#0f172a"
    bg_card       = "#1e293b"
    bg_card_hover = "#334155"
    border_color  = "#334155"
    text_primary  = "#f1f5f9"
    text_secondary= "#94a3b8"
    text_muted    = "#64748b"
    divider_color = "#334155"
    table_head_bg = "#1e293b"
    table_head_fg = "#94a3b8"
    table_row_alt = "#1e293b"
    summary_bg    = "#0c2231"
    summary_border= "#1e4a66"
    success_bg    = "#052e16"
    error_bg      = "#1c0a0a"
    warning_bg    = "#1c1200"
    plotly_paper  = "rgba(15,23,42,0)"
    plotly_plot   = "rgba(15,23,42,0)"
    grid_color    = "#1e293b"
    compare_header= "#0f172a"
else:
    bg_main       = "#ffffff"
    bg_card       = "#f8fafc"
    bg_card_hover = "#f1f5f9"
    border_color  = "#e2e8f0"
    text_primary  = "#0f172a"
    text_secondary= "#475569"
    text_muted    = "#94a3b8"
    divider_color = "#e2e8f0"
    table_head_bg = "#f1f5f9"
    table_head_fg = "#64748b"
    table_row_alt = "#f8fafc"
    summary_bg    = "#f0f9ff"
    summary_border= "#bae6fd"
    success_bg    = "#f0fdf4"
    error_bg      = "#fef2f2"
    warning_bg    = "#fffbeb"
    plotly_paper  = "rgba(0,0,0,0)"
    plotly_plot   = "rgba(0,0,0,0)"
    grid_color    = "#f1f5f9"
    compare_header= "#1e293b"

st.markdown(f"""
<style>
    /* ── Global overrides ── */
    .stApp {{
        background-color: {bg_main} !important;
    }}
    .stApp > header {{
        background-color: {bg_main} !important;
    }}
    /* Main content area */
    section[data-testid="stMain"] {{
        background-color: {bg_main} !important;
    }}
    section[data-testid="stMain"] > div {{
        background-color: {bg_main} !important;
    }}
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {bg_card} !important;
    }}
    /* All text */
    .stApp p, .stApp span, .stApp label, .stApp div,
    .stMarkdown, .stMarkdown p, .stMarkdown span {{
        color: {text_primary} !important;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
    }}
    /* Radio buttons */
    .stRadio label span {{
        color: {text_primary} !important;
    }}
    /* Selectbox */
    .stSelectbox > div > div {{
        background-color: {bg_card} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
    }}
    .stSelectbox svg {{
        fill: {text_secondary} !important;
    }}
    /* Selectbox dropdown options */
    [data-baseweb="select"] > div {{
        background-color: {bg_card} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
    }}
    [data-baseweb="popover"] ul {{
        background-color: {bg_card} !important;
    }}
    [data-baseweb="popover"] li {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    [data-baseweb="popover"] li:hover {{
        background-color: {bg_card_hover} !important;
    }}
    /* Dividers */
    hr {{
        border-color: {divider_color} !important;
        opacity: 1 !important;
    }}
    /* Info / success / error boxes */
    .stAlert {{
        background-color: {bg_card} !important;
        border-color: {border_color} !important;
        color: {text_primary} !important;
    }}
    /* Toggle button */
    .dark-toggle-btn {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        border-radius: 999px;
        border: 1.5px solid {border_color};
        background: {bg_card};
        color: {text_primary};
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
    }}
    .dark-toggle-btn:hover {{
        background: {bg_card_hover};
        border-color: #6366f1;
    }}
    /* Metric cards */
    .metric-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }}
    .metric-label {{
        font-size: 10px;
        font-weight: 700;
        color: {text_muted};
        text-transform: uppercase;
        letter-spacing: .08em;
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 900;
        margin: 4px 0;
    }}
    .metric-sub {{ font-size: 11px; color: {text_muted}; }}
    .compare-header {{
        background: {compare_header};
        color: #fff;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }}
    .summary-box {{
        background: {summary_bg};
        border: 1px solid {summary_border};
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 13px;
        line-height: 1.8;
        color: {text_primary};
    }}
    .up   {{ color:#10b981; font-weight:700; }}
    .down {{ color:#ef4444; font-weight:700; }}
    .same {{ color:{text_muted}; font-weight:700; }}

    /* Error table rows */
    .row-success {{ background: {success_bg} !important; }}
    .row-error   {{ background: {error_bg}   !important; }}
    .row-warning {{ background: {warning_bg} !important; }}
    .row-purple  {{ background: {"#1a0a2e" if dark else "#faf5ff"} !important; }}
    .row-neutral {{ background: {bg_card}    !important; }}

    table.detail-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        color: {text_primary};
    }}
    table.detail-table thead tr {{
        background: {table_head_bg};
        color: {table_head_fg};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
    }}
    table.detail-table th,
    table.detail-table td {{
        padding: 10px 14px;
        border-bottom: 1px solid {border_color};
    }}
    table.detail-table th {{ text-align: left; }}
    table.detail-table td:nth-child(2),
    table.detail-table td:nth-child(3) {{ text-align: right; }}
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
    {"key":"w1","label":"W1  —  18/02 – 22/02","total":120,"success":94, "failed":26,"bot":20,"captcha":2,"pdf":3,"generic":1},
    {"key":"w2","label":"W2  —  23/02 – 01/03","total":165,"success":137,"failed":28,"bot":22,"captcha":2,"pdf":3,"generic":1},
    {"key":"w3","label":"W3  —  02/03 – 08/03","total":165,"success":138,"failed":27,"bot":21,"captcha":2,"pdf":3,"generic":1},
    {"key":"w4","label":"W4  ★  Current  —  09/03 – 15/03","total":195,"success":168,"failed":27,"bot":22,"captcha":2,"pdf":3,"generic":0},
]
ALL_TIME = {
    "key":"all","label":"All Time  —  18/02 – 15/03",
    "total":645,"success":537,"failed":108,
    "bot":85,"captcha":8,"pdf":12,"generic":3
}
ALL_DATA  = WEEKS + [ALL_TIME]
OPTIONS   = [w["label"] for w in ALL_DATA]

avg_gen_time = 40
if stats and stats.get("avg_gen_time"):
    avg_gen_time = round(float(stats["avg_gen_time"]))

today_total   = 0
today_success = 0
today_failed  = 0
if stats and stats.get("today"):
    today_total   = int(stats["today"].get("total")   or 0)
    today_success = int(stats["today"].get("success") or 0)
    today_failed  = int(stats["today"].get("failed")  or 0)

def get_data(label):
    return next(x for x in ALL_DATA if x["label"] == label)

def success_rate(d): return round(d["success"] / d["total"] * 100, 1)
def error_rate(d):   return round(d["failed"]  / d["total"] * 100, 1)
def bot_pct(d):      return round(d["bot"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def captcha_pct(d):  return round(d["captcha"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def pdf_pct(d):      return round(d["pdf"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def generic_pct(d):  return round(d["generic"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0

# ── Header + Toggle ───────────────────────────────────────────────────────────
header_col, toggle_col = st.columns([5, 1])
with header_col:
    st.markdown("## 📊 Content Pipeline · Executive Dashboard")
    st.markdown(f"*Generated {date.today().strftime('%d %B %Y')} · Live data refreshes every 60 seconds*")
with toggle_col:
    st.markdown("<br>", unsafe_allow_html=True)
    toggle_label = "☀️ Light Mode" if dark else "🌙 Dark Mode"
    if st.button(toggle_label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.divider()

# ── Mode toggle ───────────────────────────────────────────────────────────────
mode = st.radio("**View mode**", ["Single Period", "Compare Two Periods"], horizontal=True)
st.divider()

# ── Plotly layout helper ──────────────────────────────────────────────────────
def plotly_base_layout(**kwargs):
    return dict(
        paper_bgcolor=plotly_paper,
        plot_bgcolor=plotly_plot,
        font=dict(color=text_primary),
        yaxis=dict(gridcolor=grid_color, color=text_secondary),
        xaxis=dict(gridcolor=grid_color, color=text_secondary),
        **kwargs
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE PERIOD VIEW
# ═══════════════════════════════════════════════════════════════════════════════
if mode == "Single Period":

    selected = st.selectbox("**Period**", OPTIONS, index=3)
    d = get_data(selected)

    sr  = success_rate(d)
    er  = error_rate(d)
    bp  = bot_pct(d)
    cp  = captcha_pct(d)
    pp  = pdf_pct(d)
    gp  = generic_pct(d)
    excl_bot       = d["captcha"] + d["pdf"] + d["generic"]
    er_without_bot = round(excl_bot / d["total"] * 100, 1)
    processing_mins = round(avg_gen_time * d["total"] / 60)
    period_label   = "this week" if d["key"] != "all" else "all time"

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    vol_label = "Weekly Volume" if d["key"] != "all" else "Total Volume"
    vol_sub   = "articles this week" if d["key"] != "all" else "articles all time"

    with c1:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #6366f1;"><div class="metric-label">{vol_label}</div><div class="metric-value" style="color:#6366f1;">{d["total"]}</div><div class="metric-sub">{vol_sub}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #10b981;"><div class="metric-label">Success Rate</div><div class="metric-value" style="color:#10b981;">{sr}%</div><div class="metric-sub">{d["success"]} of {d["total"]} articles</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #f59e0b;"><div class="metric-label">Avg Gen Time</div><div class="metric-value" style="color:#f59e0b;">{avg_gen_time}s</div><div class="metric-sub">per article (live)</div></div>', unsafe_allow_html=True)
    with c4:
        tc = "#94a3b8" if today_total == 0 else "#f59e0b"
        ts = "no articles yet today" if today_total == 0 else f"{today_success} success · {today_failed} failed"
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #f59e0b;"><div class="metric-label">Today\'s Output</div><div class="metric-value" style="color:{tc};">{today_total}</div><div class="metric-sub">{ts}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #ef4444;"><div class="metric-label">Error Rate</div><div class="metric-value" style="color:#ef4444;">{er}%</div><div class="metric-sub">{d["failed"]} of {d["total"]} failed</div></div>', unsafe_allow_html=True)

    st.divider()

    # Charts
    col_bar, col_donut = st.columns([3, 2])
    with col_bar:
        st.markdown(f"**Volume by Outcome — {d['label']}**")
        bar = go.Figure(go.Bar(
            x=["No Errors","Bot Protection","CAPTCHA","PDF Timeout","Generic"],
            y=[d["success"],d["bot"],d["captcha"],d["pdf"],d["generic"]],
            marker_color=["#10b981","#ef4444","#8b5cf6","#f59e0b","#6b7280"]
        ))
        bar.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=250, showlegend=False,
                          **plotly_base_layout())
        st.plotly_chart(bar, use_container_width=True)
    with col_donut:
        st.markdown("**Distribution**")
        donut = go.Figure(go.Pie(
            labels=["No Errors","Bot Protection","PDF Timeout","CAPTCHA","Generic"],
            values=[d["success"],d["bot"],d["pdf"],d["captcha"],d["generic"]],
            hole=0.6, marker_colors=["#10b981","#ef4444","#f59e0b","#8b5cf6","#6b7280"]
        ))
        donut.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=250,
                            paper_bgcolor=plotly_paper,
                            font=dict(color=text_primary),
                            legend=dict(font=dict(size=10, color=text_primary)))
        st.plotly_chart(donut, use_container_width=True)

    st.divider()

    # Error trends line chart
    st.markdown("**Error Trends — Weekly Since Monitoring Start (18 Feb 2026)**")
    wl = [w["label"].split("—")[0].strip() for w in WEEKS]
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(name="Bot Protection",   x=wl, y=[w["bot"]     for w in WEEKS], mode="lines+markers", line=dict(color="#ef4444",width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="PDF Timeout",      x=wl, y=[w["pdf"]     for w in WEEKS], mode="lines+markers", line=dict(color="#f59e0b",width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="CAPTCHA",          x=wl, y=[w["captcha"] for w in WEEKS], mode="lines+markers", line=dict(color="#8b5cf6",width=2.5), marker=dict(size=8)))
    fig_line.add_trace(go.Scatter(name="Generic Fallback", x=wl, y=[w["generic"] for w in WEEKS], mode="lines+markers", line=dict(color="#6b7280",width=2,dash="dash"), marker=dict(size=8)))
    fig_line.update_layout(height=280, margin=dict(t=10,b=10,l=0,r=0),
                           yaxis=dict(title="Error count", gridcolor=grid_color, color=text_secondary),
                           legend=dict(orientation="h",yanchor="bottom",y=1.02,font=dict(size=11, color=text_primary)),
                           **{k:v for k,v in plotly_base_layout().items() if k not in ("yaxis",)})
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Error table
    st.markdown(f"**Error Type Detail — {d['label']}**")
    st.markdown(f"""
<table class="detail-table">
  <thead><tr>
    <th>Error Type</th>
    <th>Count</th>
    <th>Share</th>
    <th>Description & Action</th>
  </tr></thead>
  <tbody>
    <tr class="row-success"><td style="color:#16a34a;font-weight:600;">🟢 No Errors</td><td style="font-weight:700;">{d['success']}</td><td>{round(d['success']/d['total']*100,1)}%</td><td style="color:{text_secondary};">Article successfully fetched, processed and published. No action required.</td></tr>
    <tr class="row-error"><td style="color:#dc2626;font-weight:600;">🔴 Bot Protection / Access Blocked</td><td style="font-weight:700;">{d['bot']}</td><td>{bp}%</td><td style="color:{text_secondary};">Website blocked automated access. Analyst must open source manually and write update.</td></tr>
    <tr class="row-purple"><td style="color:#7c3aed;font-weight:600;">🟣 CAPTCHA / Security Check</td><td style="font-weight:700;">{d['captcha']}</td><td>{cp}%</td><td style="color:{text_secondary};">Page requires a security check. Analyst should review source and write update manually.</td></tr>
    <tr class="row-warning"><td style="color:#d97706;font-weight:600;">🟡 PDF Timeout</td><td style="font-weight:700;">{d['pdf']}</td><td>{pp}%</td><td style="color:{text_secondary};">PDF took too long to load. Analyst should review document directly and write update manually.</td></tr>
    <tr class="row-neutral"><td style="color:#475569;font-weight:600;">⚫ Generic Fallback</td><td style="font-weight:700;">{d['generic']}</td><td>{gp}%</td><td style="color:{text_secondary};">Source could not be accessed automatically. Analyst to review source manually.</td></tr>
  </tbody>
</table>""", unsafe_allow_html=True)

    st.divider()

    # Footer cards
    f1, f2, f3 = st.columns(3)
    with f1:
        st.info(f"⚡ **Pipeline Speed**\n\nAverage **{avg_gen_time} seconds** per article. At {d['total']} articles that's ~**{processing_mins} minutes** of total processing time.")
    with f2:
        st.error(f"🚨 **Top Error Driver**\n\nBot Protection accounts for **{bp}%** of all failures. Fixing this would reduce error rate from {er}% to ~**{er_without_bot}%**.")
    with f3:
        st.success(f"📈 **Weekly Throughput**\n\n**{d['total']} articles** {period_label}. **{d['failed']} articles** required manual analyst intervention.")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARE VIEW
# ═══════════════════════════════════════════════════════════════════════════════
else:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel1 = st.selectbox("**Period A**", OPTIONS, index=2)
    with col_sel2:
        sel2 = st.selectbox("**Period B**", OPTIONS, index=3)

    a = get_data(sel1)
    b = get_data(sel2)

    sr_a, sr_b   = success_rate(a), success_rate(b)
    er_a, er_b   = error_rate(a),   error_rate(b)
    bp_a, bp_b   = bot_pct(a),      bot_pct(b)

    st.divider()

    h1, h2 = st.columns(2)
    with h1:
        st.markdown(f'<div class="compare-header">🅐 {a["label"]}</div>', unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div class="compare-header">🅑 {b["label"]}</div>', unsafe_allow_html=True)

    def kpi_card(label, val_a, val_b, unit="", higher_is_better=True, color_a="#6366f1", color_b="#6366f1"):
        diff = round(val_b - val_a, 1)
        if diff > 0:
            arrow = "▲" if higher_is_better else "▼"
            diff_color = "#10b981" if higher_is_better else "#ef4444"
        elif diff < 0:
            arrow = "▼" if higher_is_better else "▲"
            diff_color = "#ef4444" if higher_is_better else "#10b981"
        else:
            arrow, diff_color = "→", "#94a3b8"
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card" style="border-left:4px solid {color_a};"><div class="metric-label">{label}</div><div class="metric-value" style="color:{color_a};">{val_a}{unit}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card" style="border-left:4px solid {color_b};"><div class="metric-value" style="color:{color_b};">{val_b}{unit}</div><div class="metric-sub" style="color:{diff_color};font-weight:700;">{arrow} {abs(diff)}{unit} vs Period A</div></div>', unsafe_allow_html=True)

    kpi_card("Total Articles",  a["total"],   b["total"],   higher_is_better=True,  color_a="#6366f1", color_b="#6366f1")
    kpi_card("Success Rate",    sr_a,         sr_b,         unit="%", higher_is_better=True,  color_a="#10b981", color_b="#10b981")
    kpi_card("Error Rate",      er_a,         er_b,         unit="%", higher_is_better=False, color_a="#ef4444", color_b="#ef4444")
    kpi_card("Failed Articles", a["failed"],  b["failed"],  higher_is_better=False, color_a="#ef4444", color_b="#ef4444")
    kpi_card("Bot Errors",      a["bot"],     b["bot"],     higher_is_better=False, color_a="#ef4444", color_b="#ef4444")
    kpi_card("PDF Timeouts",    a["pdf"],     b["pdf"],     higher_is_better=False, color_a="#f59e0b", color_b="#f59e0b")
    kpi_card("CAPTCHA Errors",  a["captcha"], b["captcha"], higher_is_better=False, color_a="#8b5cf6", color_b="#8b5cf6")

    st.divider()

    ch1, ch2 = st.columns(2)
    for col, d, lbl in [(ch1, a, "A"), (ch2, b, "B")]:
        with col:
            fig = go.Figure(go.Bar(
                x=["No Errors","Bot","CAPTCHA","PDF","Generic"],
                y=[d["success"],d["bot"],d["captcha"],d["pdf"],d["generic"]],
                marker_color=["#10b981","#ef4444","#8b5cf6","#f59e0b","#6b7280"]
            ))
            fig.update_layout(title=f"Period {lbl} — {d['label']}", title_font_color=text_primary,
                              height=220, margin=dict(t=30,b=10,l=0,r=0), showlegend=False,
                              **plotly_base_layout())
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("### 📝 Comparison Summary")

    def trend(val_a, val_b, higher_is_better=True):
        if val_b > val_a:
            return ("improved", "up") if higher_is_better else ("worsened", "down")
        elif val_b < val_a:
            return ("declined", "down") if higher_is_better else ("improved", "up")
        else:
            return ("unchanged", "same")

    vol_trend,  vol_cls  = trend(a["total"],   b["total"])
    sr_trend,   sr_cls   = trend(sr_a,          sr_b)
    er_trend,   er_cls   = trend(er_a,          er_b,   higher_is_better=False)
    bot_trend,  bot_cls  = trend(a["bot"],      b["bot"],  higher_is_better=False)
    pdf_trend,  pdf_cls  = trend(a["pdf"],      b["pdf"],  higher_is_better=False)
    cap_trend,  cap_cls  = trend(a["captcha"],  b["captcha"], higher_is_better=False)

    vol_diff  = b["total"]   - a["total"]
    sr_diff   = round(sr_b   - sr_a,  1)
    er_diff   = round(er_b   - er_a,  1)
    bot_diff  = b["bot"]     - a["bot"]
    pdf_diff  = b["pdf"]     - a["pdf"]
    cap_diff  = b["captcha"] - a["captcha"]

    def fmt_diff(val, cls):
        sign = "+" if val > 0 else ""
        return f'<span class="{cls}">{sign}{val}</span>'

    summary_html = f"""
<div class="summary-box">
<strong>Period A:</strong> {a['label']} &nbsp;|&nbsp; <strong>Period B:</strong> {b['label']}<br><br>

📦 <strong>Volume:</strong> Article output {vol_trend} from <strong>{a['total']}</strong> to <strong>{b['total']}</strong> ({fmt_diff(vol_diff, vol_cls)} articles).<br><br>

✅ <strong>Success Rate:</strong> {sr_trend.capitalize()} from <strong>{sr_a}%</strong> to <strong>{sr_b}%</strong> ({fmt_diff(sr_diff, sr_cls)}pp) — 
{'a positive trend showing pipeline reliability is increasing.' if sr_cls == 'up' else 'success rate fell, worth investigating the cause.' if sr_cls == 'down' else 'no change in pipeline reliability.'}<br><br>

❌ <strong>Error Rate:</strong> {er_trend.capitalize()} from <strong>{er_a}%</strong> to <strong>{er_b}%</strong> ({fmt_diff(er_diff, er_cls)}pp).<br><br>

🤖 <strong>Bot Protection errors</strong> {bot_trend} from <strong>{a['bot']}</strong> to <strong>{b['bot']}</strong> ({fmt_diff(bot_diff, bot_cls)}) — 
{'this remains the top error driver and the primary focus for remediation.' if b['bot'] > b['pdf'] and b['bot'] > b['captcha'] else 'bot protection is no longer the top error driver.'}<br><br>

🟡 <strong>PDF Timeouts</strong> {pdf_trend} ({fmt_diff(pdf_diff, pdf_cls)}) &nbsp;·&nbsp; 
🟣 <strong>CAPTCHA errors</strong> {cap_trend} ({fmt_diff(cap_diff, cap_cls)}).<br><br>

{'⚠️ <strong>Watch:</strong> Error rate increased period-on-period. Review source access patterns.' if er_cls == 'down' else '✅ <strong>Positive:</strong> Overall pipeline performance improved between these two periods.' if sr_cls == 'up' else '➡️ Performance was broadly stable between these two periods.'}
</div>"""

    st.markdown(summary_html, unsafe_allow_html=True)
