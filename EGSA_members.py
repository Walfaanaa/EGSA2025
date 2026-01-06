# =======================================================
# 🏦 EGSA 2025 Management System  (NET CAPITAL – FIXED)
# =======================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="EGSA 2025 Cash Flow Management System",
    layout="wide"
)

load_dotenv()
PASSWORD = os.getenv("EGSA_PASSWORD", "1234")

# ---------------- PASSWORD GATE ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 EGSA 2025 Login")
    pwd = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access granted")
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.stop()

# ---------------- LOGO ----------------
logo_path = "EGSA.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{logo_base64}" width="200">
            <h1 style="color:#2c3e50;">EGSA 2025 Q2 Management System</h1>
            <div style="color:gray;">Net Capital & Performance Tracking</div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.title("EGSA 2025 Q2 Management System")
    st.caption("Net Capital & Performance Tracking")

# ---------------- LOAD DATA ----------------
file_path = "EGSA2025_info_w.xlsx"
df = None

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
else:
    uploaded = st.file_uploader("📤 Upload Q2 Excel File", type=["xlsx", "xls"])
    if uploaded:
        df = pd.read_excel(uploaded)

if df is None:
    st.warning("❌ No Excel file loaded.")
    st.stop()

# ---------------- CLEAN DATA ----------------
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

if "name" not in df.columns:
    st.error("❌ 'name' column missing.")
    st.stop()

df["name"] = df["name"].astype(str).str.strip()
df = df[~df["name"].str.contains("total", case=False, na=False)]
df = df.drop_duplicates()

numeric_cols = [
    "monthly_payment_q2",
    "q2_plan",
    "q2_achievement",
    "fee_charge",
    "benefit_gain",
    "expenditure"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    else:
        df[col] = 0

# ---------------- COMPUTE METRICS ----------------
df["total_payment"] = (
    df["q2_achievement"]
    + df["fee_charge"]
    + df["benefit_gain"]
    - df["expenditure"]
)

df["difference_q2"] = df["q2_achievement"] - df["q2_plan"]
df["payment_rank"] = df["total_payment"].rank(
    method="dense",
    ascending=False
).astype(int)

# ---------------- DISPLAY DATA ----------------
st.subheader("📋 Q2 Member Performance (Net Capital)")
st.dataframe(df, use_container_width=True)

# ---------------- UPDATE MONTHLY PAYMENT ----------------
st.subheader("💵 Update Monthly Payment (Q2)")
c1, c2 = st.columns(2)

with c1:
    member_name = st.selectbox("Select Member", df["name"])

with c2:
    added_payment = st.number_input(
        "Enter Amount to Add (ETB)",
        min_value=0,
        step=100
    )

if st.button("✅ Update Payment"):
    df.loc[df["name"] == member_name, "monthly_payment_q2"] += added_payment
    st.success(f"Payment updated for **{member_name}**")

# ---------------- SUMMARY METRICS ----------------
st.subheader("📊 Summary Metrics (Net)")

Q2_plan = df["q2_plan"].sum()
Q2_achievement = df["q2_achievement"].sum()
T_monthly = df["monthly_payment_q2"].sum()
T_fee = df["fee_charge"].sum()
T_benefit = df["benefit_gain"].sum()
T_expenditure = df["expenditure"].sum()

G_total = (
    Q2_achievement
    + T_fee
    + T_benefit
    - T_expenditure
)

cols = st.columns(7)
cols[0].metric("Q2 Plan", f"{Q2_plan:,.0f}")
cols[1].metric(
    "Q2 Achievement",
    f"{Q2_achievement:,.0f}",
    delta=int(Q2_achievement - Q2_plan)
)
cols[2].metric("Monthly Payment Q2", f"{T_monthly:,.0f}")
cols[3].metric("Fee Charge", f"{T_fee:,.0f}")
cols[4].metric("Benefit Gain", f"{T_benefit:,.0f}")
cols[5].metric("Expenditure", f"-{T_expenditure:,.0f}")
cols[6].metric("Net Grand Total", f"{G_total:,.0f}")

# ---------------- BAR CHART (NEGATIVES OK) ----------------
st.subheader("📊 Financial Overview – Inflow vs Outflow")

bar_totals = {
    "Q2 Achievement": Q2_achievement,
    "Fee Charge": T_fee,
    "Benefit Gain": T_benefit,
    "Expenditure": -T_expenditure,
    "Net Capital": G_total
}

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(bar_totals.keys(), bar_totals.values())
ax.set_ylabel("Amount (ETB)")
ax.set_title("EGSA 2025 Q2 – Net Financial Overview")

fig, ax = plt.subplots(figsize=(10, 5))

colors = [
    "#2ecc71",  # Q2 Achievement (green)
    "#3498db",  # Fee Charge (blue)
    "#9b59b6",  # Benefit Gain (purple)
    "#e74c3c",  # Expenditure (red - outflow)
    "#f1c40f"   # Net Capital (gold)
]

ax.bar(
    bar_totals.keys(),
    bar_totals.values(),
    color=colors
)

ax.set_ylabel("Amount (ETB)")
ax.set_title("EGSA 2025 Q2 – Net Financial Overview")


# ---------------- PIE CHART (NO NEGATIVES) ----------------
st.subheader("📊 Financial Composition (Positive Values Only)")

pie_totals = {
    "Q2 Achievement": Q2_achievement,
    "Fee Charge": T_fee,
    "Benefit Gain": T_benefit,
    "Expenditure": T_expenditure
}

fig2, ax2 = plt.subplots(figsize=(7, 7))
ax2.pie(
    pie_totals.values(),
    labels=pie_totals.keys(),
    autopct="%1.1f%%",
    startangle=140
)
ax2.set_title("EGSA 2025 Q2 – Financial Composition")
ax2.axis("equal")
st.pyplot(fig2)

# ---------------- FINAL REPORT ----------------
total_row = pd.DataFrame({
    "name": ["🟩 TOTAL 🟩"],
    "monthly_payment_q2": [T_monthly],
    "q2_plan": [Q2_plan],
    "q2_achievement": [Q2_achievement],
    "fee_charge": [T_fee],
    "benefit_gain": [T_benefit],
    "expenditure": [T_expenditure],
    "total_payment": [G_total],
    "difference_q2": [Q2_achievement - Q2_plan],
    "payment_rank": [None]
})

final_df = pd.concat([df, total_row], ignore_index=True)

st.subheader("📗 Final Q2 Report (Net Capital)")
st.dataframe(final_df, use_container_width=True)

# ---------------- DOWNLOAD ----------------
buffer = BytesIO()
final_df.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)

st.download_button(
    label="💾 Download Updated Excel",
    data=buffer,
    file_name="EGSA2025_Q2_NET_Report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

