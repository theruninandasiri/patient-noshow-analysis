
import base64
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import streamlit as st

st.set_page_config(page_title="No-Show Analysis", layout="wide")

def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg = get_base64("bg.jpg")
st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: 'Times New Roman', Times, serif !important; }}
            
.stApp {{
    background-image: url("data:image/jpg;base64,{bg}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(8, 25, 50, 0.82);
    z-index: 0;
}}
.block-container {{
    position: relative;
    z-index: 1;
    padding: 0 2rem 2rem 2rem !important;
    max-width: 1200px;
}}
#MainMenu, footer, header {{ visibility: hidden; }}

.banner {{
    background: linear-gradient(90deg, rgba(10,61,107,0.95) 0%, rgba(26,122,196,0.9) 100%);
    border-radius: 0 0 20px 20px;
    padding: 1.8rem 2.2rem 1.6rem;
    margin: 0 -2rem 2rem -2rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}}
.banner h1 {{ color:#fff !important; font-size:1.45rem !important; font-weight:700 !important; margin:0 0 0.3rem 0 !important; }}
.banner p  {{ color:#7FB3D9 !important; font-size:0.82rem !important; margin:0 !important; }}
.banner-badge {{
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    color: #B8D9F5;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
}}

.kpi-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:1.5rem; }}
.kpi {{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius:14px;
    padding:1.2rem 1.4rem;
    border:1px solid rgba(255,255,255,0.15);
    position:relative;
    overflow:hidden;
}}
.kpi::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; background:#1A7AC4; border-radius:14px 14px 0 0; }}
.kpi.red::before   {{ background:#E05A2B; }}
.kpi.green::before {{ background:#1A9E6A; }}
.kpi-icon  {{ font-size:1.3rem; margin-bottom:0.4rem; display:block; }}
.kpi-label {{ font-size:0.69rem; color:#7FB3D9; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:5px; }}
.kpi-value {{ font-size:2rem; font-weight:700; color:#ffffff; line-height:1; }}
.kpi.red   .kpi-value {{ color:#FF7A52; }}
.kpi.green .kpi-value {{ color:#3DD68C; }}
.kpi-sub   {{ font-size:0.71rem; color:#6EA8D0; margin-top:5px; }}

.chart-card {{
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius:14px;
    border:1px solid rgba(255,255,255,0.13);
    padding:1.3rem 1.5rem 1rem;
    margin-bottom:1.2rem;
}}
.chart-title {{
    font-size:0.69rem;
    font-weight:700;
    color:#7FB3D9;
    text-transform:uppercase;
    letter-spacing:0.08em;
    margin-bottom:0.9rem;
    padding-bottom:0.7rem;
    border-bottom:1px solid rgba(255,255,255,0.1);
}}

.pill {{ border-radius:8px; padding:0.65rem 0.95rem; margin-bottom:9px; font-size:0.81rem; line-height:1.5; display:flex; align-items:flex-start; gap:0.55rem; }}
.pill-icon {{ flex-shrink:0; margin-top:1px; }}
.pill.red   {{ background:rgba(224,90,43,0.15); border-left:3px solid #E05A2B; color:#FFBFA8; }}
.pill.green {{ background:rgba(26,158,106,0.15); border-left:3px solid #1A9E6A; color:#A0EBC9; }}

[data-testid="stSidebar"] {{
    background: rgba(8,25,50,0.88) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.1) !important;
}}
[data-testid="stSidebar"] > div {{ padding-top:1.5rem; }}
[data-testid="stSidebar"] label {{ font-size:0.72rem !important; color:#7FB3D9 !important; font-weight:600 !important; text-transform:uppercase !important; letter-spacing:0.06em !important; }}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: #B8D9F5 !important; }}
.sidebar-logo {{ background: linear-gradient(135deg, #0A3D6B, #1A7AC4); border-radius:10px; padding:0.9rem 1rem; margin-bottom:1.2rem; text-align:center; }}
.sidebar-logo span {{ color:#fff; font-weight:700; font-size:0.9rem; }}
.sidebar-logo p {{ color:#B8D9F5; font-size:0.72rem; margin:2px 0 0; }}
</style>
""", unsafe_allow_html=True)

BLUE  = "#1A7AC4"
CORAL = "#E05A2B"
TEAL  = "#1A9E6A"
MGRAY = "#7FB3D9"

def style_ax(ax, grid_axis="y"):
    ax.set_facecolor("#0D1F35")
    ax.figure.patch.set_facecolor("#0D1F35")
    ax.spines[["top","right"]].set_visible(False)
    ax.spines[["left","bottom"]].set_color("#1E3A5F")
    ax.tick_params(colors="#7FB3D9", labelsize=9)
    ax.xaxis.label.set_color("#7FB3D9")
    ax.yaxis.label.set_color("#7FB3D9")
    if grid_axis == "y":
        ax.grid(axis="y", color="#1E3A5F", linewidth=0.8, zorder=0)
        ax.grid(axis="x", visible=False)
    else:
        ax.grid(axis="x", color="#1E3A5F", linewidth=0.8, zorder=0)
        ax.grid(axis="y", visible=False)

@st.cache_data
def load_data():
    df = pd.read_csv("KaggleV2-May-2016.csv")
    df.rename(columns={
        "PatientId":"patient_id","AppointmentID":"appointment_id",
        "Gender":"gender","ScheduledDay":"scheduled_day",
        "AppointmentDay":"appointment_day","Age":"age",
        "Neighbourhood":"neighbourhood","Scholarship":"scholarship",
        "Hipertension":"hypertension","Diabetes":"diabetes",
        "Alcoholism":"alcoholism","Handcap":"handicap",
        "SMS_received":"sms_received","No-show":"no_show",
    }, inplace=True)
    df["scheduled_day"]   = pd.to_datetime(df["scheduled_day"],   utc=True)
    df["appointment_day"] = pd.to_datetime(df["appointment_day"], utc=True)
    df = df[df["age"] >= 0]
    df["no_show_flag"] = (df["no_show"] == "Yes").astype(int)
    df["wait_days"]    = (df["appointment_day"] - df["scheduled_day"]).dt.days
    df = df[df["wait_days"] >= 0]
    df["appt_weekday"] = df["appointment_day"].dt.day_name()
    bins   = [0,10,18,30,45,60,80,120]
    labels = ["0-10","11-18","19-30","31-45","46-60","61-80","80+"]
    df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)
    return df

df = load_data()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><span>NoShow Analyser</span><p>Vitória, Brazil · 2016</p></div>', unsafe_allow_html=True)
    st.markdown("**Filters**")
    selected_gender = st.selectbox("Gender", ["All","Female","Male"])
    selected_age    = st.selectbox("Age Group", ["All","0-10","11-18","19-30","31-45","46-60","61-80","80+"])
    selected_sms    = st.selectbox("SMS Reminder", ["All","SMS Received","No SMS"])
    weekday_order   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    selected_days   = st.multiselect("Days of Week", weekday_order, default=weekday_order)
    st.divider()
    st.markdown("**Dataset**")
    st.markdown("[Medical Appointment No Shows →](https://www.kaggle.com/datasets/joniarroba/noshowappointments)")
    st.caption("110,527 records · Kaggle")

filtered = df.copy()
if selected_gender != "All":
    filtered = filtered[filtered["gender"] == selected_gender[0]]
if selected_age != "All":
    filtered = filtered[filtered["age_group"] == selected_age]
if selected_sms == "SMS Received":
    filtered = filtered[filtered["sms_received"] == 1]
elif selected_sms == "No SMS":
    filtered = filtered[filtered["sms_received"] == 0]
if selected_days:
    filtered = filtered[filtered["appt_weekday"].isin(selected_days)]
if len(filtered) == 0:
    st.warning("No data matches the selected filters.")
    st.stop()

st.markdown("""
<div class="banner">
  <div>
    <h1> Patient Appointment No-Show Analysis</h1>
    <p>Identifying patterns in missed appointments to improve healthcare resource planning</p>
  </div>
  <div class="banner-badge"> EDA + SQL</div>
</div>
""", unsafe_allow_html=True)

total        = len(filtered)
noshow_count = int(filtered["no_show_flag"].sum())
noshow_rate  = filtered["no_show_flag"].mean() * 100
avg_wait     = filtered["wait_days"].mean()

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi">
    <span class="kpi-icon">∑</span>
    <div class="kpi-label">Total Appointments</div>
    <div class="kpi-value">{total:,}</div>
    <div class="kpi-sub">across 81 neighbourhoods</div>
  </div>
  <div class="kpi red">
    <span class="kpi-icon">％</span>
    <div class="kpi-label">No-Show Rate</div>
    <div class="kpi-value">{noshow_rate:.1f}%</div>
    <div class="kpi-sub">{noshow_count:,} missed appointments</div>
  </div>
  <div class="kpi green">
    <span class="kpi-icon">✔</span>
    <div class="kpi-label">Show-Up Rate</div>
    <div class="kpi-value">{100-noshow_rate:.1f}%</div>
    <div class="kpi-sub">{total-noshow_count:,} attended</div>
  </div>
  <div class="kpi">
    <span class="kpi-icon">⌛︎</span>
    <div class="kpi-label">Avg Wait Time</div>
    <div class="kpi-value">{avg_wait:.1f}d</div>
    <div class="kpi-sub">scheduled to appointment</div>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="chart-card"><div class="chart-title">No-Show Rate by Age Group</div>', unsafe_allow_html=True)
    age_rate = filtered.groupby("age_group", observed=True)["no_show_flag"].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 3.2))
    clrs = [CORAL if v == age_rate.max() else BLUE for v in age_rate.values]
    bars = ax.bar(age_rate.index, age_rate.values, color=clrs, edgecolor="#0D1F35", width=0.62, zorder=3)
    style_ax(ax)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("Age Group"); ax.set_ylabel("No-Show Rate")
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.45,
                f"{bar.get_height():.1f}%", ha="center", fontsize=8, color=MGRAY)
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-card"><div class="chart-title">No-Show Rate by Day of Week</div>', unsafe_allow_html=True)
    avail    = [d for d in weekday_order if d in selected_days]
    day_rate = (filtered[filtered["appt_weekday"].isin(avail)]
                .groupby("appt_weekday")["no_show_flag"].mean()
                .reindex(avail) * 100)
    fig, ax = plt.subplots(figsize=(6, 3.2))
    clrs = [CORAL if v == day_rate.max() else BLUE for v in day_rate.values]
    bars = ax.bar(day_rate.index, day_rate.values, color=clrs, edgecolor="#0D1F35", width=0.62, zorder=3)
    style_ax(ax)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.tick_params(axis="x", rotation=20)
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.25,
                f"{bar.get_height():.1f}%", ha="center", fontsize=8, color=MGRAY)
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="chart-card"><div class="chart-title">Impact of SMS Reminders</div>', unsafe_allow_html=True)
    sms_rate = filtered.groupby("sms_received")["no_show_flag"].mean() * 100
    sms_rate.index = ["No SMS", "SMS Sent"]
    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    bars = ax.bar(sms_rate.index, sms_rate.values,
                  color=[CORAL, TEAL], edgecolor="#0D1F35", width=0.42, zorder=3)
    style_ax(ax)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, max(sms_rate.values)*1.3)
    ax.bar_label(bars, fmt="%.1f%%", padding=5, fontsize=12, color="#ffffff", fontweight="bold")
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-card"><div class="chart-title">No-Show Rate by Wait Time</div>', unsafe_allow_html=True)
    filtered2 = filtered.copy()
    wait_bins   = [0,1,8,15,31,999]
    wait_labels = ["Same day","1-7 days","8-14 days","15-30 days","30+ days"]
    filtered2["wait_bucket"] = pd.cut(filtered2["wait_days"], bins=wait_bins, labels=wait_labels, right=False)
    wait_rate = filtered2.groupby("wait_bucket", observed=True)["no_show_flag"].mean() * 100
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(range(len(wait_rate)), wait_rate.values,
            marker="o", color=BLUE, linewidth=2.5, markersize=8, zorder=3)
    ax.fill_between(range(len(wait_rate)), wait_rate.values, alpha=0.15, color=BLUE)
    for i, v in enumerate(wait_rate.values):
        ax.text(i, v+1.1, f"{v:.1f}%", ha="center", fontsize=8, color=MGRAY)
    style_ax(ax)
    ax.set_xticks(range(len(wait_rate)))
    ax.set_xticklabels(wait_rate.index, rotation=12, fontsize=8)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Neighbourhoods by No-Show Rate (min. 100 appointments)</div>', unsafe_allow_html=True)
neigh = (filtered.groupby("neighbourhood")
         .agg(total=("no_show_flag","count"), rate=("no_show_flag","mean"))
         .query("total >= 100")
         .sort_values("rate", ascending=False)
         .head(10))
neigh["pct"] = neigh["rate"] * 100
fig, ax = plt.subplots(figsize=(10, 3.4))
clrs = [CORAL] + [BLUE]*(len(neigh)-1)
ax.barh(neigh.index[::-1], neigh["pct"][::-1], color=clrs[::-1], edgecolor="#0D1F35", height=0.58, zorder=3)
style_ax(ax, grid_axis="x")
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
for i, val in enumerate(neigh["pct"][::-1]):
    ax.text(val+0.15, i, f"{val:.1f}%", va="center", fontsize=9, color=MGRAY)
fig.tight_layout()
st.pyplot(fig); plt.close(fig)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chart-card"><div class="chart-title">Key Insights & Recommendations</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("***Risk Factors***")
    st.markdown("""
    <div class='pill red'><span class='pill-icon'>⚠︎</span>Teenagers (11–18) have the highest no-show rate — they need dedicated reminder strategies.</div>
    <div class='pill red'><span class='pill-icon'>⚠︎</span>Patients waiting 30+ days are over 7x more likely to no-show than same-day patients (33% vs 4.6%).</div>
    <div class='pill red'><span class='pill-icon'>⚠︎</span>Low-income (Scholarship) patients no-show more — likely due to transport or financial barriers.</div>
    <div class='pill red'><span class='pill-icon'>⚠︎</span>Santos Dumont neighbourhood has the worst no-show rate at 28.9%.</div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("***Recommendations***")
    st.markdown("""
    <div class='pill green'><span class='pill-icon'>✔</span>Prioritise same-day or short-wait scheduling — dramatically reduces no-show risk.</div>
    <div class='pill green'><span class='pill-icon'>✔</span>Expand SMS reminders targeting teenagers and high-risk neighbourhoods.</div>
    <div class='pill green'><span class='pill-icon'>✔</span>Investigate transport or financial support options for Scholarship patients.</div>
    <div class='pill green'><span class='pill-icon'>✔</span>Patients aged 60+ are the most reliable — safe to schedule back-to-back.</div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Explore Raw Data"):
    st.dataframe(
        filtered[["gender","age","age_group","neighbourhood",
                  "wait_days","sms_received","hypertension","diabetes","no_show"]].head(500),
        use_container_width=True
    )
    st.caption(f"Showing first 500 of {len(filtered):,} filtered records.")