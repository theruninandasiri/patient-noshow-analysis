"""
=============================================================
 Patient Appointment No-Show Analysis — SQL Analysis
 Uses SQLite (built into Python, no installation needed)
 Run: python noshow_sql.py
 Results saved to outputs/sql_results/
=============================================================
"""

import pandas as pd
import sqlite3
import os

# ── Config ───────────────────────────────────────────────────────────────────
DATA_FILE = "KaggleV2-May-2016.csv"
DB_FILE   = "noshow.db"
OUT_DIR   = "outputs/sql_results"
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD CSV INTO SQLITE DATABASE
# ─────────────────────────────────────────────────────────────────────────────
print("📂 Loading CSV into SQLite database...")

df = pd.read_csv(DATA_FILE)

df.rename(columns={
    "PatientId":      "patient_id",
    "AppointmentID":  "appointment_id",
    "Gender":         "gender",
    "ScheduledDay":   "scheduled_day",
    "AppointmentDay": "appointment_day",
    "Age":            "age",
    "Neighbourhood":  "neighbourhood",
    "Scholarship":    "scholarship",
    "Hipertension":   "hypertension",
    "Diabetes":       "diabetes",
    "Alcoholism":     "alcoholism",
    "Handcap":        "handicap",
    "SMS_received":   "sms_received",
    "No-show":        "no_show",
}, inplace=True)

df["no_show_flag"] = (df["no_show"] == "Yes").astype(int)
df["scheduled_day"]   = pd.to_datetime(df["scheduled_day"],   utc=True).dt.date.astype(str)
df["appointment_day"] = pd.to_datetime(df["appointment_day"], utc=True).dt.date.astype(str)
df = df[df["age"] >= 0]

conn = sqlite3.connect(DB_FILE)
df.to_sql("appointments", conn, if_exists="replace", index=False)
print(f"✅ Database created: {DB_FILE}")
print(f"   Total records loaded: {len(df):,}\n")


# ─────────────────────────────────────────────────────────────────────────────
# HELPER — run query, print result, save to CSV
# ─────────────────────────────────────────────────────────────────────────────
def run_query(title, sql, filename):
    print(f"🔍 {title}")
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))
    path = os.path.join(OUT_DIR, filename)
    result.to_csv(path, index=False)
    print(f"   💾 Saved → {path}\n")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Q1. What is the overall no-show rate?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q1: Overall no-show rate",
    """
    SELECT
        COUNT(*)                                      AS total_appointments,
        SUM(no_show_flag)                             AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)             AS noshow_rate_pct
    FROM appointments
    """,
    "q1_overall_noshow_rate.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q2. Does sending an SMS reminder reduce no-shows?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q2: SMS reminder impact on no-show rate",
    """
    SELECT
        CASE WHEN sms_received = 1 THEN 'SMS Sent' ELSE 'No SMS' END AS sms_status,
        COUNT(*)                                   AS total_appointments,
        SUM(no_show_flag)                          AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)          AS noshow_rate_pct
    FROM appointments
    GROUP BY sms_received
    ORDER BY sms_received
    """,
    "q2_sms_impact.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q3. Which neighbourhoods have the highest no-show rates?
#     (minimum 100 appointments to filter low-volume areas)
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q3: Top 10 neighbourhoods by no-show rate (min 100 appointments)",
    """
    SELECT
        neighbourhood,
        COUNT(*)                              AS total_appointments,
        SUM(no_show_flag)                     AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)     AS noshow_rate_pct
    FROM appointments
    GROUP BY neighbourhood
    HAVING COUNT(*) >= 100
    ORDER BY noshow_rate_pct DESC
    LIMIT 10
    """,
    "q3_top_neighbourhoods.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q4. Which day of the week has the most no-shows?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q4: No-show rate by day of week",
    """
    SELECT
        CASE CAST(strftime('%w', appointment_day) AS INTEGER)
            WHEN 0 THEN '7-Sunday'
            WHEN 1 THEN '1-Monday'
            WHEN 2 THEN '2-Tuesday'
            WHEN 3 THEN '3-Wednesday'
            WHEN 4 THEN '4-Thursday'
            WHEN 5 THEN '5-Friday'
            WHEN 6 THEN '6-Saturday'
        END AS weekday,
        COUNT(*)                              AS total_appointments,
        SUM(no_show_flag)                     AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)     AS noshow_rate_pct
    FROM appointments
    GROUP BY weekday
    ORDER BY weekday
    """,
    "q4_noshow_by_weekday.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q5. How does wait time affect no-show rates?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q5: No-show rate by wait time bucket",
    """
    SELECT
        CASE
            WHEN julianday(appointment_day) - julianday(scheduled_day) = 0  THEN '0 days (same day)'
            WHEN julianday(appointment_day) - julianday(scheduled_day) <= 7  THEN '1-7 days'
            WHEN julianday(appointment_day) - julianday(scheduled_day) <= 14 THEN '8-14 days'
            WHEN julianday(appointment_day) - julianday(scheduled_day) <= 30 THEN '15-30 days'
            ELSE '30+ days'
        END AS wait_bucket,
        COUNT(*)                              AS total_appointments,
        SUM(no_show_flag)                     AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)     AS noshow_rate_pct
    FROM appointments
    WHERE julianday(appointment_day) - julianday(scheduled_day) >= 0
    GROUP BY wait_bucket
    ORDER BY MIN(julianday(appointment_day) - julianday(scheduled_day))
    """,
    "q5_noshow_by_wait_time.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q6. Does having a health condition affect no-show rates?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q6: No-show rate by health condition",
    """
    SELECT 'Hypertension' AS condition,
        ROUND(AVG(CASE WHEN hypertension = 1 THEN no_show_flag END) * 100, 2) AS with_condition_pct,
        ROUND(AVG(CASE WHEN hypertension = 0 THEN no_show_flag END) * 100, 2) AS without_condition_pct
    FROM appointments
    UNION ALL
    SELECT 'Diabetes',
        ROUND(AVG(CASE WHEN diabetes = 1 THEN no_show_flag END) * 100, 2),
        ROUND(AVG(CASE WHEN diabetes = 0 THEN no_show_flag END) * 100, 2)
    FROM appointments
    UNION ALL
    SELECT 'Alcoholism',
        ROUND(AVG(CASE WHEN alcoholism = 1 THEN no_show_flag END) * 100, 2),
        ROUND(AVG(CASE WHEN alcoholism = 0 THEN no_show_flag END) * 100, 2)
    FROM appointments
    UNION ALL
    SELECT 'Scholarship (Bolsa Familia)',
        ROUND(AVG(CASE WHEN scholarship = 1 THEN no_show_flag END) * 100, 2),
        ROUND(AVG(CASE WHEN scholarship = 0 THEN no_show_flag END) * 100, 2)
    FROM appointments
    """,
    "q6_noshow_by_condition.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q7. What age group has the highest no-show rate?
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q7: No-show rate by age group",
    """
    SELECT
        CASE
            WHEN age BETWEEN 0  AND 10  THEN '0-10'
            WHEN age BETWEEN 11 AND 18  THEN '11-18'
            WHEN age BETWEEN 19 AND 30  THEN '19-30'
            WHEN age BETWEEN 31 AND 45  THEN '31-45'
            WHEN age BETWEEN 46 AND 60  THEN '46-60'
            WHEN age BETWEEN 61 AND 80  THEN '61-80'
            ELSE '80+'
        END AS age_group,
        COUNT(*)                              AS total_appointments,
        SUM(no_show_flag)                     AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)     AS noshow_rate_pct
    FROM appointments
    GROUP BY age_group
    ORDER BY MIN(age)
    """,
    "q7_noshow_by_age.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# Q8. Gender breakdown
# ─────────────────────────────────────────────────────────────────────────────
run_query(
    "Q8: No-show rate by gender",
    """
    SELECT
        CASE gender WHEN 'F' THEN 'Female' ELSE 'Male' END AS gender,
        COUNT(*)                              AS total_appointments,
        SUM(no_show_flag)                     AS total_noshows,
        ROUND(AVG(no_show_flag) * 100, 2)     AS noshow_rate_pct
    FROM appointments
    GROUP BY gender
    """,
    "q8_noshow_by_gender.csv"
)


# ─────────────────────────────────────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────────────────────────────────────
conn.close()
print("=" * 55)
print("  ✅ All SQL queries complete!")
print(f"  📁 Results saved to ./{OUT_DIR}/")
print("  📊 Open any CSV file in Excel to view the tables.")
print("=" * 55)
