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

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-label { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: .08em; }
    .metric-value { font-size: 2rem; font-weight: 900; margin: 4px 0; }
    .metric-sub   { font-size: 11px; color: #94a3b8; }
    .green  { color: #10b981; }
    .red    { color: #ef4444; }
    .orange { color: #f59e0b; }
    .grey   { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── Fetch live API data ───────────────────────────────────────────────────────
API_URL = "http://18.170.93.124:5000/api/stats"

@st.cache_data(ttl=60)
def fetch_stats():
    try:
        r = requests.get(API_URL, timeout=10)
        return r.json()
    except Exception:
        return None

stats = fetch_stats()

# ── Weekly historical data ────────────────────────────────────────────────────
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

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 Content Pipeline · Executive Dashboard")
st.markdown(f"*Generated {date.today().strftime('%d %B %Y')} · Data refreshes every 60 seconds*")
st.divider()

# ── Period selector ───────────────────────────────────────────────────────────
options = [w["label"] for w in WEEKS] + [ALL_TIME["label"]]
all_data = WEEKS + [ALL_TIME]
selected_label = st.selectbox("**Period**", options, index=3)
d = next(x for x in all_data if x["label"] == selected_label)

success_rate = round(d["success"] / d["total"] * 100, 1)
error_rate   = round(d["failed"]  / d["total"] * 100, 1)
bot_pct      = round(d["bot"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
captcha_pct  = round(d["captcha"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0
pdf_pct      = round(d["pdf"]     / d["failed"] * 100, 1) if d["failed"] > 0 else 0
generic_pct  = round(d["generic"] / d["failed"] * 100, 1) if d["failed"] > 0 else 0

# ── Live today data from API ──────────────────────────────────────────────────
today_total   = 0
today_success = 0
today_failed  = 0
avg_gen_time  = 40
if stats:
    if stats.get("today"):
        today_total   = int(stats["today"].get("total")   or 0)
        today_success = int(stats["today"].get("success") or 0)
        today_failed  = int(stats["today"].get("failed")  or 0)
    if stats.get("avg_gen_time"):
        avg_gen_time = round(float(stats["avg_gen_time"]))

# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

vol_label = "Weekly Volume" if d["key"] != "all" else "Total Volume"
vol_sub   = "articles this week" if d["key"] != "all" else "articles all time"

with c1:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid #6366f1;">
        <div class="metric-label">{vol_label}</div>
        <div class="metric-value" style="color:#6366f1;">{d['total']}</div>
        <div class="metric-sub">{vol_sub}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid #10b981;">
        <div class="metric-label">Success Rate</div>
        <div class="metric-value green">{success_rate}%</div>
        <div class="metric-sub">{d['success']} of {d['total']} articles</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid #f59e0b;">
        <div class="metric-label">Avg Gen Time</div>
        <div class="metric-value orange">{avg_gen_time}s</div>
        <div class="metric-sub">per article (live)</div>
    </div>""", unsafe_allow_html=True)

with c4:
    today_sub = "no articles yet today" if today_total == 0 else f"{today_success} success · {today_failed} failed"
    today_color = "#94a3b8" if today_total == 0 else "#f59e0b"
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid #f59e0b;">
        <div class="metric-label">Today's Output</div>
        <div class="metric-value" style="color:{today_color};">{today_total}</div>
        <div class="metric-sub">{today_sub}</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid #ef4444;">
        <div class="metric-label">Error Rate</div>
        <div class="metric-value red">{error_rate}%</div>
        <div class="metric-sub">{d['failed']} of {d['total']} failed</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── Charts row ────────────────────────────────────────────────────────────────
col_bar, col_donut = st.columns([3, 2])

with col_bar:
    st.markdown(f"**Volume by Outcome — {d['label']}**")
    bar = go.Figure(go.Bar(
        x=["No Errors", "Bot Protection", "CAPTCHA", "PDF Timeout", "Generic"],
        y=[d["success"], d["bot"], d["captcha"], d["pdf"], d["generic"]],
        marker_color=["#10b981", "#ef4444", "#8b5cf6", "#f59e0b", "#6b7280"]
    ))
    bar.update_layout(
        margin=dict(t=10, b=10, l=0, r=0),
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#f1f5f9")
    )
    st.plotly_chart(bar, use_container_width=True)

with col_donut:
    st.markdown("**Distribution**")
    donut = go.Figure(go.Pie(
        labels=["No Errors", "Bot Protection", "PDF Timeout", "CAPTCHA", "Generic"],
        values=[d["success"], d["bot"], d["pdf"], d["captcha"], d["generic"]],
        hole=0.6,
        marker_colors=["#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#6b7280"]
    ))
    donut.update_layout(
        margin=dict(t=10, b=10, l=0, r=0),
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(size=10))
    )
    st.plotly_chart(donut, use_container_width=True)

st.divider()

# ── Error Trends Line Chart ───────────────────────────────────────────────────
st.markdown("**Error Trends — Weekly Since Monitoring Start (18 Feb 2026)**")

week_labels = [w["label"].split("—")[0].strip() for w in WEEKS]
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(name="Bot Protection",   x=week_labels, y=[w["bot"]     for w in WEEKS], mode="lines+markers", line=dict(color="#ef4444", width=2.5), marker=dict(size=8)))
fig_line.add_trace(go.Scatter(name="PDF Timeout",      x=week_labels, y=[w["pdf"]     for w in WEEKS], mode="lines+markers", line=dict(color="#f59e0b", width=2.5), marker=dict(size=8)))
fig_line.add_trace(go.Scatter(name="CAPTCHA",          x=week_labels, y=[w["captcha"] for w in WEEKS], mode="lines+markers", line=dict(color="#8b5cf6", width=2.5), marker=dict(size=8)))
fig_line.add_trace(go.Scatter(name="Generic Fallback", x=week_labels, y=[w["generic"] for w in WEEKS], mode="lines+markers", line=dict(color="#6b7280", width=2,   dash="dash"), marker=dict(size=8)))
fig_line.update_layout(
    height=280,
    margin=dict(t=10, b=10, l=0, r=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#f1f5f9", title="Error count"),
    xaxis=dict(gridcolor="#f1f5f9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11))
)
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ── Error Type Detail Table ───────────────────────────────────────────────────
st.markdown(f"**Error Type Detail — {d['label']}**")

table_data = {
    "Error Type":        ["✅ No Errors", "🔴 Bot Protection / Access Blocked", "🟣 CAPTCHA / Security Check", "🟡 PDF Timeout", "⚫ Generic Fallback"],
    "Count":             [d["success"], d["bot"], d["captcha"], d["pdf"], d["generic"]],
    "Share":             [f"{round(d['success']/d['total']*100,1)}%", f"{bot_pct}%", f"{captcha_pct}%", f"{pdf_pct}%", f"{generic_pct}%"],
    "Description":       [
        "Article successfully fetched, processed and published.",
        "Website blocked automated access. Open source and create update manually.",
        "Page requires a security check. Review source and write update manually.",
        "PDF took too long to load. Review document and write update manually.",
        "Could not access source automatically. Review source manually."
    ]
}
st.dataframe(table_data, use_container_width=True, hide_index=True)

st.divider()

# ── Footer info cards ─────────────────────────────────────────────────────────
f1, f2, f3 = st.columns(3)
with f1:
    st.info(f"⚡ **Pipeline Speed**\n\nAverage **{avg_gen_time} seconds** per article. At {WEEKS[3]['total']} articles/week that's ~**{round(avg_gen_time * WEEKS[3]['total'] / 60)} minutes** of processing time.")
with f2:
    st.error(f"🚨 **Top Error Driver**\n\nBot Protection accounts for **{round(ALL_TIME['bot']/ALL_TIME['failed']*100,1)}%** of all failures. Fixing this would reduce error rate from {round(ALL_TIME['failed']/ALL_TIME['total']*100,1)}% to ~**{round(ALL_TIME['generic']+ALL_TIME['captcha']+ALL_TIME['pdf'])/ALL_TIME['total']*100:.1f}%**.")
with f3:
    st.success(f"📈 **Weekly Throughput**\n\n**{WEEKS[3]['total']} articles** this week. ~**{round(WEEKS[3]['failed']*1.2)} articles** require manual analyst intervention at current error rates.")
