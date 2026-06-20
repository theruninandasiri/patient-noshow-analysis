"""
=============================================================
 Patient Appointment No-Show Analysis
 Dataset: Medical Appointment No Shows (Kaggle)
 Link: https://www.kaggle.com/datasets/joniarroba/noshowappointments
=============================================================
 Instructions:
   1. Download the dataset CSV from Kaggle (link above)
   2. Save it as 'KaggleV2-May-2016.csv' in the same folder as this script
   3. Run: pip install pandas matplotlib seaborn
   4. Run: python noshow_eda.py
   All charts will be saved as PNG files in an 'outputs/' folder.
=============================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

# ── Config ───────────────────────────────────────────────────────────────────
DATA_FILE = "KaggleV2-May-2016.csv"
OUT_DIR   = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
COLORS = {"show": "#4C9BE8", "noshow": "#E8694C"}

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
print("📂 Loading data...")
df = pd.read_csv(DATA_FILE)

# Rename columns for readability
df.rename(columns={
    "PatientId":        "patient_id",
    "AppointmentID":    "appointment_id",
    "Gender":           "gender",
    "ScheduledDay":     "scheduled_day",
    "AppointmentDay":   "appointment_day",
    "Age":              "age",
    "Neighbourhood":    "neighbourhood",
    "Scholarship":      "scholarship",
    "Hipertension":     "hypertension",
    "Diabetes":         "diabetes",
    "Alcoholism":       "alcoholism",
    "Handcap":          "handicap",
    "SMS_received":     "sms_received",
    "No-show":          "no_show",
}, inplace=True)

# Parse dates
df["scheduled_day"]   = pd.to_datetime(df["scheduled_day"],   utc=True)
df["appointment_day"] = pd.to_datetime(df["appointment_day"], utc=True)

# Drop invalid ages
df = df[df["age"] >= 0]

# Encode no-show as binary  (1 = did NOT show up)
df["no_show_flag"] = (df["no_show"] == "Yes").astype(int)

# Wait time in days
df["wait_days"] = (df["appointment_day"] - df["scheduled_day"]).dt.days
df = df[df["wait_days"] >= 0]   # remove scheduling errors

# Day of week of appointment
df["appt_weekday"] = df["appointment_day"].dt.day_name()
WEEKDAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

print(f"✅ Dataset shape: {df.shape}")
print(f"   No-show rate: {df['no_show_flag'].mean():.1%}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 2. HELPER
# ─────────────────────────────────────────────────────────────────────────────
def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"   💾 Saved → {path}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 3. OVERALL NO-SHOW RATE
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 1: Overall no-show rate...")
show_pct   = 1 - df["no_show_flag"].mean()
noshow_pct = df["no_show_flag"].mean()

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(
    [show_pct, noshow_pct],
    labels=["Showed Up", "No-Show"],
    colors=[COLORS["show"], COLORS["noshow"]],
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 13},
)
ax.set_title("Overall Appointment Attendance", fontsize=15, fontweight="bold", pad=15)
save(fig, "01_overall_noshow_rate.png")


# ─────────────────────────────────────────────────────────────────────────────
# 4. NO-SHOW RATE BY GENDER
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 2: No-show rate by gender...")
gender_rate = df.groupby("gender")["no_show_flag"].mean().reset_index()
gender_rate["gender"] = gender_rate["gender"].map({"F": "Female", "M": "Male"})

fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(gender_rate["gender"], gender_rate["no_show_flag"] * 100,
              color=[COLORS["noshow"], COLORS["show"]], width=0.4, edgecolor="white")
ax.set_ylim(0, 30)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=11)
ax.set_title("No-Show Rate by Gender", fontsize=14, fontweight="bold")
ax.set_xlabel("Gender"); ax.set_ylabel("No-Show Rate")
save(fig, "02_noshow_by_gender.png")


# ─────────────────────────────────────────────────────────────────────────────
# 5. NO-SHOW RATE BY AGE GROUP
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 3: No-show rate by age group...")
bins   = [0, 10, 18, 30, 45, 60, 80, 120]
labels = ["0-10","11-18","19-30","31-45","46-60","61-80","80+"]
df["age_group"] = pd.cut(df["age"], bins=bins, labels=labels, right=True)

age_rate = df.groupby("age_group", observed=True)["no_show_flag"].mean() * 100

fig, ax = plt.subplots(figsize=(9, 4))
age_rate.plot(kind="bar", ax=ax, color=COLORS["noshow"], edgecolor="white", width=0.6)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("No-Show Rate by Age Group", fontsize=14, fontweight="bold")
ax.set_xlabel("Age Group"); ax.set_ylabel("No-Show Rate")
ax.tick_params(axis="x", rotation=0)
for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{bar.get_height():.1f}%", ha="center", fontsize=9)
save(fig, "03_noshow_by_age_group.png")


# ─────────────────────────────────────────────────────────────────────────────
# 6. NO-SHOW RATE BY DAY OF WEEK
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 4: No-show rate by day of week...")
day_rate = (
    df[df["appt_weekday"].isin(WEEKDAY_ORDER)]
    .groupby("appt_weekday")["no_show_flag"]
    .mean()
    .reindex(WEEKDAY_ORDER) * 100
)

fig, ax = plt.subplots(figsize=(9, 4))
day_rate.plot(kind="bar", ax=ax, color=COLORS["show"], edgecolor="white", width=0.6)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("No-Show Rate by Day of Week", fontsize=14, fontweight="bold")
ax.set_xlabel("Day of Appointment"); ax.set_ylabel("No-Show Rate")
ax.tick_params(axis="x", rotation=15)
for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f"{bar.get_height():.1f}%", ha="center", fontsize=9)
save(fig, "04_noshow_by_weekday.png")


# ─────────────────────────────────────────────────────────────────────────────
# 7. SMS REMINDER IMPACT
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 5: Impact of SMS reminders...")
sms_rate = df.groupby("sms_received")["no_show_flag"].mean() * 100
sms_rate.index = ["No SMS", "SMS Sent"]

fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(sms_rate.index, sms_rate.values,
              color=[COLORS["show"], COLORS["noshow"]], width=0.4, edgecolor="white")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_ylim(0, 35)
ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=12)
ax.set_title("No-Show Rate: SMS Reminder vs. No Reminder", fontsize=13, fontweight="bold")
ax.set_ylabel("No-Show Rate")
save(fig, "05_sms_reminder_impact.png")


# ─────────────────────────────────────────────────────────────────────────────
# 8. WAIT TIME VS NO-SHOW
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 6: Wait time distribution by outcome...")
fig, ax = plt.subplots(figsize=(9, 4))
for flag, label, color in [(0, "Showed Up", COLORS["show"]),
                            (1, "No-Show",   COLORS["noshow"])]:
    subset = df[df["no_show_flag"] == flag]["wait_days"].clip(upper=90)
    ax.hist(subset, bins=30, alpha=0.6, label=label, color=color, edgecolor="white")
ax.set_title("Wait Time Distribution by Outcome (capped at 90 days)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Wait Days (Scheduled → Appointment)")
ax.set_ylabel("Number of Appointments")
ax.legend()
save(fig, "06_wait_time_distribution.png")


# ─────────────────────────────────────────────────────────────────────────────
# 9. HEALTH CONDITIONS VS NO-SHOW
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 7: No-show rate by health condition...")
conditions = ["hypertension", "diabetes", "alcoholism", "scholarship"]
labels_map = {
    "hypertension": "Hypertension",
    "diabetes":     "Diabetes",
    "alcoholism":   "Alcoholism",
    "scholarship":  "Bolsa Família\n(Scholarship)",
}

rates_yes, rates_no = [], []
for c in conditions:
    rates_yes.append(df[df[c] == 1]["no_show_flag"].mean() * 100)
    rates_no.append( df[df[c] == 0]["no_show_flag"].mean() * 100)

x = range(len(conditions))
width = 0.35
fig, ax = plt.subplots(figsize=(10, 5))
b1 = ax.bar([i - width/2 for i in x], rates_no,  width, label="Without Condition",
             color=COLORS["show"],   edgecolor="white")
b2 = ax.bar([i + width/2 for i in x], rates_yes, width, label="With Condition",
             color=COLORS["noshow"], edgecolor="white")
ax.set_xticks(list(x))
ax.set_xticklabels([labels_map[c] for c in conditions])
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("No-Show Rate by Health Condition", fontsize=14, fontweight="bold")
ax.set_ylabel("No-Show Rate")
ax.legend()
ax.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=8)
ax.bar_label(b2, fmt="%.1f%%", padding=3, fontsize=8)
save(fig, "07_noshow_by_condition.png")


# ─────────────────────────────────────────────────────────────────────────────
# 10. TOP 10 NEIGHBOURHOODS BY NO-SHOW RATE
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Chart 8: Top 10 neighbourhoods by no-show rate...")
neigh = (
    df.groupby("neighbourhood")
    .agg(total=("no_show_flag", "count"), noshow_rate=("no_show_flag", "mean"))
    .query("total >= 100")       # filter low-volume neighbourhoods
    .sort_values("noshow_rate", ascending=False)
    .head(10)
)
neigh["noshow_rate_pct"] = neigh["noshow_rate"] * 100

fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(neigh.index[::-1], neigh["noshow_rate_pct"][::-1],
        color=COLORS["noshow"], edgecolor="white")
ax.xaxis.set_major_formatter(mtick.PercentFormatter())
ax.set_title("Top 10 Neighbourhoods by No-Show Rate\n(min. 100 appointments)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("No-Show Rate")
for i, (val, name) in enumerate(zip(neigh["noshow_rate_pct"][::-1], neigh.index[::-1])):
    ax.text(val + 0.2, i, f"{val:.1f}%", va="center", fontsize=9)
save(fig, "08_top_neighbourhoods.png")


# ─────────────────────────────────────────────────────────────────────────────
# 11. SUMMARY STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  KEY FINDINGS SUMMARY")
print("="*55)
print(f"  Total appointments  : {len(df):,}")
print(f"  Overall no-show rate: {df['no_show_flag'].mean():.1%}")
print(f"  No-show w/ SMS      : {df[df.sms_received==1]['no_show_flag'].mean():.1%}")
print(f"  No-show w/o SMS     : {df[df.sms_received==0]['no_show_flag'].mean():.1%}")
print(f"  Avg wait (show)     : {df[df.no_show_flag==0]['wait_days'].mean():.1f} days")
print(f"  Avg wait (no-show)  : {df[df.no_show_flag==1]['wait_days'].mean():.1f} days")
print(f"  Highest-risk age    : {age_rate.idxmax()} ({age_rate.max():.1f}%)")
print("="*55)
print(f"\n✅ All charts saved to ./{OUT_DIR}/\n")
