# 🏥 Patient Appointment No-Show Analysis

## 📌 Project Overview
This project analyzes **110,527 medical appointments** from public hospitals in Vitória, Brazil to identify patterns in patient no-shows and provide actionable recommendations to reduce missed appointments.

## 🎯 Business Problem
Missed appointments cost hospitals significant time and resources. This analysis answers:
- Who is most likely to miss an appointment?
- Does sending an SMS reminder help?
- Which neighbourhoods have the highest no-show rates?
- How does wait time affect attendance?

## 🛠️ Tools & Technologies
- **Python** — pandas, matplotlib, seaborn
- **SQL** — SQLite (8 business queries)
- **Streamlit** — interactive dashboard
- **Excel** — SQL results exported as CSV

## 📊 Key Findings
| Finding | Detail |
|---|---|
| Overall no-show rate | 20.2% (22,319 missed appointments) |
| Highest risk age group | Teenagers 11–18 (25.3% no-show rate) |
| Wait time impact | 30+ day wait = 33% no-show vs 4.6% same day |
| Worst neighbourhood | Santos Dumont (28.9% no-show rate) |
| SMS reminder effect | Patients with SMS had higher no-show — suggests SMS targets at-risk patients |

## ✅ Recommendations
1. **Reduce scheduling gaps** — same-day appointments have only 4.6% no-show rate
2. **Target teenagers** with dedicated SMS reminders
3. **Investigate transport support** for low-income (Scholarship) patients
4. **Focus outreach** on high-risk neighbourhoods like Santos Dumont

## 📁 Project Structure
noshow_project/

├── noshow_eda.py        # Exploratory Data Analysis (8 charts)

├── noshow_sql.py        # SQL business queries (8 queries)

├── dashboard.py         # Interactive Streamlit dashboard

└── outputs/

├── *.png            # EDA charts

└── sql_results/     # Query results as CSV

## 🚀 How to Run
```bash
# Install dependencies
pip install pandas matplotlib seaborn streamlit

# Run EDA
python noshow_eda.py

# Run SQL analysis
python noshow_sql.py

# Launch dashboard
python -m streamlit run dashboard.py
```

## 📂 Dataset
[Medical Appointment No Shows — Kaggle](https://www.kaggle.com/datasets/joniarroba/noshowappointments)