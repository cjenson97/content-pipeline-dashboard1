import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import date, timedelta
import io
import csv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Content Pipeline · Exec Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Dark mode toggle ──────────────────────────────────────────────────────────
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=False)

BG      = "#0f172a" if dark_mode else "#ffffff"
BG2     = "#1e293b" if dark_mode else "#f8fafc"
BORDER  = "#334155" if dark_mode else "#e2e8f0"
TEXT    = "#f1f5f9" if dark_mode else "#1e293b"
SUBTEXT = "#94a3b8" if dark_mode else "#64748b"
CHART_BG = "#1e293b" if dark_mode else "rgba(0,0,0,0)"

st.markdown(f"""
<style>
    .stApp {{ background-color: {BG} !important; }}
    .block-container {{ background-color: {BG} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {BG2} !important; }}
    p, h1, h2, h3, h4, label, .stMarkdown {{ color: {TEXT} !important; }}
    hr {{ border-color: {BORDER} !important; }}
    .stSelectbox > div > div {{ background-color: {BG2} !important; color: {TEXT} !important; border-color: {BORDER} !important; }}
    .stRadio > div {{ color: {TEXT} !important; }}
    .stAlert {{ background-color: {BG2} !important; border-color: {BORDER} !important; color: {TEXT} !important; }}
    .stDownloadButton button {{ background-color: {BG2} !important; color: {TEXT} !important; border-color: {BORDER} !important; }}
    .stDateInput > div > div {{ background-color: {BG2} !important; color: {TEXT} !important; border-color: {BORDER} !important; }}

    .metric-card {{
        background: {BG2};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        height: 100%;
    }}
    .metric-label {{ font-size: 10px; font-weight: 700; color: {SUBTEXT}; text-transform: uppercase; letter-spacing: .08em; }}
    .metric-value {{ font-size: 2rem; font-weight: 900; margin: 4px 0; }}
    .metric-sub   {{ font-size: 11px; color: {SUBTEXT}; }}

    .compare-header {{
        background: #1e293b;
        color: #fff;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }}
    .summary-box {{
        background: {"#1e293b" if dark_mode else "#f0f9ff"};
        border: 1px solid {"#334155" if dark_mode else "#bae6fd"};
        border-radius: 12px;
        padding: 16px 20px;
        font-size: 13px;
        line-height: 1.8;
        color: {TEXT};
    }}
    .today-banner {{
        background: {"#1e3a5f" if dark_mode else "#eff6ff"};
        border: 1px solid {"#1d4ed8" if dark_mode else "#bfdbfe"};
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 13px;
        color: {TEXT};
        margin-bottom: 8px;
    }}
    .up   {{ color: #10b981; font-weight: 700; }}
    .down {{ color: #ef4444; font-weight: 700; }}
    .same {{ color: #94a3b8; font-weight: 700; }}
    table {{ color: {TEXT} !important; }}
    td, th {{ color: {TEXT} !important; border-color: {BORDER} !important; }}
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
ALL_DATA = WEEKS + [ALL_TIME]
OPTIONS  = [w["label"] for w in ALL_DATA]

def get_data(label):
    return next(x for x in ALL_DATA if x["label"] == label)

def success_rate(d): return round(d["success"] / d["total"] * 100, 1) if d["total"] > 0 else 0
def error_rate(d):   return round(d["failed"]  / d["total"] * 100, 1) if d["total"] > 0 else 0
def bot_pct(d):      return round(d["bot"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def captcha_pct(d):  return round(d["captcha"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def pdf_pct(d):      return round(d["pdf"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
def generic_pct(d):  return round(d["generic"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0

# ── Reusable chart builder ────────────────────────────────────────────────────
def make_bar(d, title=""):
    fig = go.Figure(go.Bar(
        x=["No Errors","Bot Protection","CAPTCHA","PDF Timeout","Generic"],
        y=[d["success"],d["bot"],d["captcha"],d["pdf"],d["generic"]],
        marker_color=["#10b981","#ef4444","#8b5cf6","#f59e0b","#6b7280"]
    ))
    fig.update_layout(
        title=title, height=250, margin=dict(t=30,b=10,l=0,r=0),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        showlegend=False,
        yaxis=dict(gridcolor=BORDER, color=TEXT),
        xaxis=dict(color=TEXT),
        font=dict(color=TEXT)
    )
    return fig

def make_donut(d):
    fig = go.Figure(go.Pie(
        labels=["No Errors","Bot Protection","PDF Timeout","CAPTCHA","Generic"],
        values=[d["success"],d["bot"],d["pdf"],d["captcha"],d["generic"]],
        hole=0.6, marker_colors=["#10b981","#ef4444","#f59e0b","#8b5cf6","#6b7280"]
    ))
    fig.update_layout(
        height=250, margin=dict(t=10,b=10,l=0,r=0),
        paper_bgcolor=CHART_BG,
        legend=dict(font=dict(size=10, color=TEXT)),
        font=dict(color=TEXT)
    )
    return fig

def make_trend():
    wl = [w["label"].split("—")[0].strip() for w in WEEKS]
    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Bot Protection",   x=wl, y=[w["bot"]     for w in WEEKS], mode="lines+markers", line=dict(color="#ef4444",width=2.5), marker=dict(size=8)))
    fig.add_trace(go.Scatter(name="PDF Timeout",      x=wl, y=[w["pdf"]     for w in WEEKS], mode="lines+markers", line=dict(color="#f59e0b",width=2.5), marker=dict(size=8)))
    fig.add_trace(go.Scatter(name="CAPTCHA",          x=wl, y=[w["captcha"] for w in WEEKS], mode="lines+markers", line=dict(color="#8b5cf6",width=2.5), marker=dict(size=8)))
    fig.add_trace(go.Scatter(name="Generic Fallback", x=wl, y=[w["generic"] for w in WEEKS], mode="lines+markers", line=dict(color="#6b7280",width=2,dash="dash"), marker=dict(size=8)))
    fig.update_layout(
        height=280, margin=dict(t=10,b=10,l=0,r=0),
        paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        yaxis=dict(gridcolor=BORDER, title="Error count", color=TEXT),
        xaxis=dict(gridcolor=BORDER, color=TEXT),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11, color=TEXT)),
        font=dict(color=TEXT)
    )
    return fig

# ── Reusable KPI cards row ────────────────────────────────────────────────────
def render_kpi_cards(d, show_today=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    sr = success_rate(d)
    er = error_rate(d)
    vol_label = "Weekly Volume" if d["key"] not in ["all","today"] else ("Total Volume" if d["key"]=="all" else "Today's Volume")
    vol_sub   = "articles this week" if d["key"] not in ["all","today"] else ("articles all time" if d["key"]=="all" else "articles today")

    with c1:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #6366f1;"><div class="metric-label">{vol_label}</div><div class="metric-value" style="color:#6366f1;">{d["total"]}</div><div class="metric-sub">{vol_sub}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #10b981;"><div class="metric-label">Success Rate</div><div class="metric-value" style="color:#10b981;">{sr}%</div><div class="metric-sub">{d["success"]} of {d["total"]} articles</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #f59e0b;"><div class="metric-label">Avg Gen Time</div><div class="metric-value" style="color:#f59e0b;">{avg_gen_time}s</div><div class="metric-sub">per article (live)</div></div>', unsafe_allow_html=True)
    with c4:
        if show_today:
            tc = "#94a3b8" if today_total == 0 else "#f59e0b"
            ts = "no articles yet today" if today_total == 0 else f"{today_success} success · {today_failed} failed"
            st.markdown(f'<div class="metric-card" style="border-left:4px solid #f59e0b;"><div class="metric-label">Today\'s Output</div><div class="metric-value" style="color:{tc};">{today_total}</div><div class="metric-sub">{ts}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-card" style="border-left:4px solid #f59e0b;"><div class="metric-label">Today\'s Output</div><div class="metric-value" style="color:#f59e0b;">{d["total"]}</div><div class="metric-sub">articles today</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card" style="border-left:4px solid #ef4444;"><div class="metric-label">Error Rate</div><div class="metric-value" style="color:#ef4444;">{er}%</div><div class="metric-sub">{d["failed"]} of {d["total"]} failed</div></div>', unsafe_allow_html=True)

# ── Reusable error table ──────────────────────────────────────────────────────
def render_error_table(d):
    bp = bot_pct(d); cp = captcha_pct(d); pp = pdf_pct(d); gp = generic_pct(d)
    st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead><tr style="background:{"#1e293b" if dark_mode else "#f1f5f9"};color:{SUBTEXT};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;">
    <th style="padding:10px 14px;text-align:left;border-bottom:1px solid {BORDER};">Error Type</th>
    <th style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};">Count</th>
    <th style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};">Share</th>
    <th style="padding:10px 14px;text-align:left;border-bottom:1px solid {BORDER};">Description & Action</th>
  </tr></thead>
  <tbody>
    <tr style="background:{"#14532d22" if dark_mode else "#f0fdf4"};"><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:#16a34a;font-weight:600;">🟢 No Errors</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};font-weight:700;color:{TEXT};">{d['success']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};color:{TEXT};">{round(d['success']/d['total']*100,1) if d['total']>0 else 0}%</td><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:{SUBTEXT};">Article successfully fetched, processed and published. No action required.</td></tr>
    <tr style="background:{"#7f1d1d22" if dark_mode else "#fef2f2"};"><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:#dc2626;font-weight:600;">🔴 Bot Protection / Access Blocked</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};font-weight:700;color:{TEXT};">{d['bot']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};color:{TEXT};">{bp}%</td><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:{SUBTEXT};">Website blocked automated access. Analyst must open source manually and write update.</td></tr>
    <tr style="background:{"#4c1d9522" if dark_mode else "#faf5ff"};"><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:#7c3aed;font-weight:600;">🟣 CAPTCHA / Security Check</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};font-weight:700;color:{TEXT};">{d['captcha']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};color:{TEXT};">{cp}%</td><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:{SUBTEXT};">Page requires a security check. Analyst should review source and write update manually.</td></tr>
    <tr style="background:{"#78350f22" if dark_mode else "#fffbeb"};"><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:#d97706;font-weight:600;">🟡 PDF Timeout</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};font-weight:700;color:{TEXT};">{d['pdf']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid {BORDER};color:{TEXT};">{pp}%</td><td style="padding:10px 14px;border-bottom:1px solid {BORDER};color:{SUBTEXT};">PDF took too long to load. Analyst should review document directly and write update manually.</td></tr>
    <tr style="background:{BG2};"><td style="padding:10px 14px;color:{SUBTEXT};font-weight:600;">⚫ Generic Fallback</td><td style="padding:10px 14px;text-align:right;font-weight:700;color:{TEXT};">{d['generic']}</td><td style="padding:10px 14px;text-align:right;color:{TEXT};">{gp}%</td><td style="padding:10px 14px;color:{SUBTEXT};">Source could not be accessed automatically. Analyst to review source manually.</td></tr>
  </tbody>
</table>""", unsafe_allow_html=True)

# ── Reusable footer cards ─────────────────────────────────────────────────────
def render_footer_cards(d):
    er = error_rate(d)
    bp = bot_pct(d)
    excl_bot       = d["captcha"] + d["pdf"] + d["generic"]
    er_without_bot = round(excl_bot / d["total"] * 100, 1) if d["total"] > 0 else 0
    processing_mins = round(avg_gen_time * d["total"] / 60)
    period_label   = "today" if d["key"] == "today" else ("all time" if d["key"] == "all" else "this week")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.info(f"⚡ **Pipeline Speed**\n\nAverage **{avg_gen_time} seconds** per article. At {d['total']} articles that's ~**{processing_mins} minutes** of total processing time.")
    with f2:
        st.error(f"🚨 **Top Error Driver**\n\nBot Protection accounts for **{bp}%** of all failures. Fixing this would reduce error rate from {er}% to ~**{er_without_bot}%**.")
    with f3:
        st.success(f"📈 **Throughput**\n\n**{d['total']} articles** {period_label}. **{d['failed']} articles** required manual analyst intervention.")

# ── Reusable export section ───────────────────────────────────────────────────
def render_export(periods, mode_label, comparison_html=""):
    st.divider()
    st.markdown("### ⬇️ Export")
    ex1, ex2 = st.columns(2)

    with ex1:
        st.markdown("**📄 Download CSV**")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Period","Total","Success","Failed","Success Rate %","Error Rate %","Bot","CAPTCHA","PDF Timeout","Generic","Bot % Failures","CAPTCHA % Failures","PDF % Failures","Generic % Failures"])
        for p in periods:
            sr = round(p["success"]/p["total"]*100,1) if p["total"]>0 else 0
            er = round(p["failed"]/p["total"]*100,1)  if p["total"]>0 else 0
            bp = round(p["bot"]/p["failed"]*100,1)     if p["failed"]>0 else 0
            cp = round(p["captcha"]/p["failed"]*100,1) if p["failed"]>0 else 0
            pp = round(p["pdf"]/p["failed"]*100,1)     if p["failed"]>0 else 0
            gp = round(p["generic"]/p["failed"]*100,1) if p["failed"]>0 else 0
            writer.writerow([p["label"],p["total"],p["success"],p["failed"],sr,er,p["bot"],p["captcha"],p["pdf"],p["generic"],bp,cp,pp,gp])
        st.download_button("⬇️ Download CSV", output.getvalue(), f"pipeline_{date.today()}.csv", "text/csv", use_container_width=True)

    with ex2:
        st.markdown("**📊 Download HTML Report**")
        rows_html = ""
        for p in periods:
            sr = round(p["success"]/p["total"]*100,1) if p["total"]>0 else 0
            er = round(p["failed"]/p["total"]*100,1)  if p["total"]>0 else 0
            bp = round(p["bot"]/p["failed"]*100,1)     if p["failed"]>0 else 0
            cp = round(p["captcha"]/p["failed"]*100,1) if p["failed"]>0 else 0
            pp = round(p["pdf"]/p["failed"]*100,1)     if p["failed"]>0 else 0
            gp = round(p["generic"]/p["failed"]*100,1) if p["failed"]>0 else 0
            rows_html += f"""
            <h2 style="color:#1e293b;border-bottom:2px solid #e2e8f0;padding-bottom:8px;">{p['label']}</h2>
            <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
              <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px;"><div style="font-size:10px;color:#64748b;font-weight:700;text-transform:uppercase;">Total</div><div style="font-size:2rem;font-weight:900;color:#6366f1;">{p['total']}</div></div>
              <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px;"><div style="font-size:10px;color:#64748b;font-weight:700;text-transform:uppercase;">Success</div><div style="font-size:2rem;font-weight:900;color:#10b981;">{sr}%</div></div>
              <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px;"><div style="font-size:10px;color:#64748b;font-weight:700;text-transform:uppercase;">Errors</div><div style="font-size:2rem;font-weight:900;color:#ef4444;">{er}%</div></div>
              <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px;"><div style="font-size:10px;color:#64748b;font-weight:700;text-transform:uppercase;">Failed</div><div style="font-size:2rem;font-weight:900;color:#ef4444;">{p['failed']}</div></div>
            </div>
            <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:24px;">
              <thead><tr style="background:#f1f5f9;color:#64748b;font-size:11px;font-weight:700;text-transform:uppercase;">
                <th style="padding:10px 14px;text-align:left;border-bottom:1px solid #e2e8f0;">Error Type</th>
                <th style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">Count</th>
                <th style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">Share</th>
              </tr></thead>
              <tbody>
                <tr style="background:#f0fdf4;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;color:#16a34a;font-weight:600;">✅ No Errors</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;font-weight:700;">{p['success']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">{round(p['success']/p['total']*100,1) if p['total']>0 else 0}%</td></tr>
                <tr style="background:#fef2f2;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;color:#dc2626;font-weight:600;">🔴 Bot Protection</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;font-weight:700;">{p['bot']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">{bp}%</td></tr>
                <tr style="background:#faf5ff;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;color:#7c3aed;font-weight:600;">🟣 CAPTCHA</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;font-weight:700;">{p['captcha']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">{cp}%</td></tr>
                <tr style="background:#fffbeb;"><td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;color:#d97706;font-weight:600;">🟡 PDF Timeout</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;font-weight:700;">{p['pdf']}</td><td style="padding:10px 14px;text-align:right;border-bottom:1px solid #e2e8f0;">{pp}%</td></tr>
                <tr style="background:#f8fafc;"><td style="padding:10px 14px;color:#475569;font-weight:600;">⚫ Generic Fallback</td><td style="padding:10px 14px;text-align:right;font-weight:700;">{p['generic']}</td><td style="padding:10px 14px;text-align:right;">{gp}%</td></tr>
              </tbody>
            </table>"""

        html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Content Pipeline · Executive Report · {date.today().strftime('%d %B %Y')}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:960px;margin:40px auto;padding:0 24px;color:#1e293b;}}</style>
</head><body>
<h1>📊 Content Pipeline · Executive Report</h1>
<p style="color:#64748b;">Generated {date.today().strftime('%d %B %Y')} · {mode_label}</p>
<hr style="border:1px solid #e2e8f0;margin:20px 0;">
{rows_html}
{f'<hr style="border:1px solid #e2e8f0;margin:20px 0;"><h2>📝 Comparison Summary</h2>{comparison_html}' if comparison_html else ''}
<hr style="border:1px solid #e2e8f0;margin:20px 0;">
<p style="color:#94a3b8;font-size:12px;">Content Pipeline · Executive Report · {date.today().strftime('%d %B %Y')}</p>
</body></html>"""
        st.download_button("⬇️ Download HTML Report", html, f"pipeline_report_{date.today()}.html", "text/html", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"## 📊 Content Pipeline · Executive Dashboard")
st.markdown(f"<span style='color:{SUBTEXT};font-size:13px;'>Generated {date.today().strftime('%d %B %Y')} · Live data refreshes every 60 seconds</span>", unsafe_allow_html=True)
st.divider()

# ── View mode ─────────────────────────────────────────────────────────────────
mode = st.radio("**View mode**", ["Single Period", "Compare Two Periods"], horizontal=True)
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE PERIOD VIEW
# ══════════════════════════════════════════════════════════════════════════════
if mode == "Single Period":

    # ── Granularity toggle ────────────────────────────────────────────────────
    granularity = st.radio("**Granularity**", ["📅 Today", "📆 Weekly", "📊 All Time"], horizontal=True)
    st.divider()

    # ─── TODAY ────────────────────────────────────────────────────────────────
    if granularity == "📅 Today":
        today_str = date.today().strftime('%d %B %Y')
        st.markdown(f"### 📅 Today — {today_str}")

        if today_total == 0:
            st.markdown(f"""
<div class="today-banner">
  📭 <strong>No articles generated yet today ({today_str}).</strong><br>
  The pipeline has not run yet or no data has been submitted today. Check back later — this page refreshes every 60 seconds.
</div>""", unsafe_allow_html=True)

        # Build today's data object from live API
        today_data = {
            "key": "today",
            "label": f"Today — {today_str}",
            "total":   today_total,
            "success": today_success,
            "failed":  today_failed,
            "bot":     0, "captcha": 0, "pdf": 0, "generic": 0
        }

        render_kpi_cards(today_data, show_today=False)
        st.divider()

        if today_total > 0:
            col_bar, col_donut = st.columns([3, 2])
            with col_bar:
                st.markdown(f"**Volume by Outcome — Today**")
                st.plotly_chart(make_bar(today_data, ""), use_container_width=True)
            with col_donut:
                st.markdown("**Distribution**")
                st.plotly_chart(make_donut(today_data), use_container_width=True)
            st.divider()
            st.markdown(f"**Error Type Detail — Today ({today_str})**")
            render_error_table(today_data)
            st.divider()
            render_footer_cards(today_data)

        st.markdown(f"<span style='color:{SUBTEXT};font-size:11px;'>⚠️ Daily error type breakdown (Bot/CAPTCHA/PDF/Generic) is not available from the API — only total counts for today are shown. Full breakdown available in Weekly and All Time views.</span>", unsafe_allow_html=True)
        render_export([today_data], f"Today — {today_str}")

    # ─── WEEKLY ───────────────────────────────────────────────────────────────
    elif granularity == "📆 Weekly":
        week_options = [w["label"] for w in WEEKS]
        selected_week = st.selectbox("**Select Week**", week_options, index=3)
        d = get_data(selected_week)

        render_kpi_cards(d)
        st.divider()

        col_bar, col_donut = st.columns([3, 2])
        with col_bar:
            st.markdown(f"**Volume by Outcome — {d['label']}**")
            st.plotly_chart(make_bar(d), use_container_width=True)
        with col_donut:
            st.markdown("**Distribution**")
            st.plotly_chart(make_donut(d), use_container_width=True)
        st.divider()

        st.markdown("**Error Trends — All Weeks Since 18 Feb 2026**")
        st.plotly_chart(make_trend(), use_container_width=True)
        st.divider()

        st.markdown(f"**Error Type Detail — {d['label']}**")
        render_error_table(d)
        st.divider()
        render_footer_cards(d)
        render_export([d], d["label"])

    # ─── ALL TIME ─────────────────────────────────────────────────────────────
    else:
        d = ALL_TIME
        render_kpi_cards(d)
        st.divider()

        col_bar, col_donut = st.columns([3, 2])
        with col_bar:
            st.markdown(f"**Volume by Outcome — All Time**")
            st.plotly_chart(make_bar(d), use_container_width=True)
        with col_donut:
            st.markdown("**Distribution**")
            st.plotly_chart(make_donut(d), use_container_width=True)
        st.divider()

        st.markdown("**Error Trends — Weekly Since 18 Feb 2026**")
        st.plotly_chart(make_trend(), use_container_width=True)
        st.divider()

        st.markdown("**Error Type Detail — All Time (18/02 – 15/03)**")
        render_error_table(d)
        st.divider()
        render_footer_cards(d)
        render_export([d], "All Time")


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE VIEW
# ══════════════════════════════════════════════════════════════════════════════
else:
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel1 = st.selectbox("**Period A**", OPTIONS, index=2)
    with col_sel2:
        sel2 = st.selectbox("**Period B**", OPTIONS, index=3)

    a = get_data(sel1)
    b = get_data(sel2)

    sr_a, sr_b = success_rate(a), success_rate(b)
    er_a, er_b = error_rate(a),   error_rate(b)
    bp_a, bp_b = bot_pct(a),      bot_pct(b)

    st.divider()

    h1, h2 = st.columns(2)
  h1, h2 = st.columns(2)
    with h1:
        st.markdown(f'<div class="compare-header">🅐 {a["label"]}</div>', unsafe_allow_html=True)
    with h2:
        st.markdown(f'<div class="compare-header">🅑 {b["label"]}</div>', unsafe_allow_html=True)

    def kpi_card(label, val_a, val_b, unit="", higher_is_better=True, color="#6366f1"):
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
            st.markdown(f'<div class="metric-card" style="border-left:4px solid {color};"><div class="metric-label">{label}</div><div class="metric-value" style="color:{color};">{val_a}{unit}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card" style="border-left:4px solid {color};"><div class="metric-value" style="color:{color};">{val_b}{unit}</div><div class="metric-sub" style="color:{diff_color};font-weight:700;">{arrow} {abs(diff)}{unit} vs Period A</div></div>', unsafe_allow_html=True)

    kpi_card("Total Articles",  a["total"],   b["total"],   higher_is_better=True,  color="#6366f1")
    kpi_card("Success Rate",    sr_a,         sr_b,         unit="%", higher_is_better=True,  color="#10b981")
    kpi_card("Error Rate",      er_a,         er_b,         unit="%", higher_is_better=False, color="#ef4444")
    kpi_card("Failed Articles", a["failed"],  b["failed"],  higher_is_better=False, color="#ef4444")
    kpi_card("Bot Errors",      a["bot"],     b["bot"],     higher_is_better=False, color="#ef4444")
    kpi_card("PDF Timeouts",    a["pdf"],     b["pdf"],     higher_is_better=False, color="#f59e0b")
    kpi_card("CAPTCHA Errors",  a["captcha"], b["captcha"], higher_is_better=False, color="#8b5cf6")

    st.divider()

    ch1, ch2 = st.columns(2)
    for col, d, lbl in [(ch1, a, "A"), (ch2, b, "B")]:
        with col:
            st.plotly_chart(make_bar(d, f"Period {lbl} — {d['label']}"), use_container_width=True)

    st.divider()

    # Auto-generated summary
    st.markdown("### 📝 Comparison Summary")

    def trend(val_a, val_b, higher_is_better=True):
        if val_b > val_a:
            return ("improved", "up") if higher_is_better else ("worsened", "down")
        elif val_b < val_a:
            return ("declined", "down") if higher_is_better else ("improved", "up")
        return ("unchanged", "same")

    vol_trend,  vol_cls  = trend(a["total"],   b["total"])
    sr_trend,   sr_cls   = trend(sr_a,          sr_b)
    er_trend,   er_cls   = trend(er_a,          er_b,   higher_is_better=False)
    bot_trend,  bot_cls  = trend(a["bot"],      b["bot"],     higher_is_better=False)
    pdf_trend,  pdf_cls  = trend(a["pdf"],      b["pdf"],     higher_is_better=False)
    cap_trend,  cap_cls  = trend(a["captcha"],  b["captcha"], higher_is_better=False)

    def fmt_diff(val, cls):
        sign = "+" if val > 0 else ""
        return f'<span class="{cls}">{sign}{val}</span>'

    vol_diff = b["total"]   - a["total"]
    sr_diff  = round(sr_b   - sr_a,  1)
    er_diff  = round(er_b   - er_a,  1)
    bot_diff = b["bot"]     - a["bot"]
    pdf_diff = b["pdf"]     - a["pdf"]
    cap_diff = b["captcha"] - a["captcha"]

    summary_html = f"""
<div class="summary-box">
<strong>Period A:</strong> {a['label']} &nbsp;|&nbsp; <strong>Period B:</strong> {b['label']}<br><br>
📦 <strong>Volume:</strong> Output {vol_trend} from <strong>{a['total']}</strong> to <strong>{b['total']}</strong> ({fmt_diff(vol_diff, vol_cls)} articles).<br><br>
✅ <strong>Success Rate:</strong> {sr_trend.capitalize()} from <strong>{sr_a}%</strong> to <strong>{sr_b}%</strong> ({fmt_diff(sr_diff, sr_cls)}pp) — {'pipeline reliability is increasing.' if sr_cls=='up' else 'success rate fell, worth investigating.' if sr_cls=='down' else 'no change in reliability.'}<br><br>
❌ <strong>Error Rate:</strong> {er_trend.capitalize()} from <strong>{er_a}%</strong> to <strong>{er_b}%</strong> ({fmt_diff(er_diff, er_cls)}pp).<br><br>
🤖 <strong>Bot Protection</strong> {bot_trend} from <strong>{a['bot']}</strong> to <strong>{b['bot']}</strong> ({fmt_diff(bot_diff, bot_cls)}) — {'remains the top error driver.' if b['bot'] > b['pdf'] and b['bot'] > b['captcha'] else 'no longer the top error driver.'}<br><br>
🟡 <strong>PDF Timeouts</strong> {pdf_trend} ({fmt_diff(pdf_diff, pdf_cls)}) &nbsp;·&nbsp; 🟣 <strong>CAPTCHA</strong> {cap_trend} ({fmt_diff(cap_diff, cap_cls)}).<br><br>
{'⚠️ <strong>Watch:</strong> Error rate increased period-on-period.' if er_cls=='down' else '✅ <strong>Positive:</strong> Overall pipeline performance improved.' if sr_cls=='up' else '➡️ Performance was broadly stable between these two periods.'}
</div>"""

    st.markdown(summary_html, unsafe_allow_html=True)

    render_export([a, b], f"{a['label']} vs {b['label']}", summary_html)
