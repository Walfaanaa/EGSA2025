# =======================================================
# 🏦 EGSA 2025 Management System (Cloud + Secure Version)
# =======================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
from dotenv import load_dotenv

# -------------------------------------------------------
# 🔐 Password Gate
# -------------------------------------------------------
st.set_page_config(page_title="EGSA 2025 Management System", layout="wide")
load_dotenv()
PASSWORD = os.getenv("EGSA_PASSWORD")

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

# -------------------------------------------------------
# 1️⃣ Display Logo and Title
# -------------------------------------------------------
logo_path = "EGSA.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = f.read()
        logo_base64 = base64.b64encode(logo_data).decode()
else:
    st.error("❌ Logo file not found! Please ensure 'EGSA.png' is in your repo.")
    st.stop()

st.markdown(f"""
<div style="text-align:center;">
    <img src="data:image/png;base64,{logo_base64}" width="200" style="animation: rotate 5s linear infinite;">
    <h1 style="color:#2c3e50;">EGSA 2025 Management System</h1>
    <div style="color:gray;font-size:1.1em;">Efficient management and performance tracking for EGSA members (2025 Edition)</div>
</div>

<style>
@keyframes rotate {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# 2️⃣ Load & Clean Data
# -------------------------------------------------------
file_path = "EGSA2025_info_w.xlsx"
if not os.path.exists(file_path):
    st.error("❌ Excel file not found! Please ensure 'EGSA2025_info_w.xlsx' is uploaded.")
    st.stop()

df = pd.read_excel(file_path)

# Standardize column names
df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
df["name"] = df["name"].astype(str).str.strip()

# Remove TOTAL rows and duplicates
df = df[~df["name"].str.contains("TOTAL", case=False, na=False)]
df = df.drop_duplicates()

# Define numeric columns
numeric_cols = ["q1_plan", "q1_achievement", "monthly_payment_q2",
                "q2_plan", "q2_achievement", "fee_charge", "voluntary_saving",
                "benefit_gain", "expenditure"]

# Clean numeric columns safely
for col in numeric_cols:
    if col in df.columns:
        # Convert to numeric, keep actual numbers, fill blanks with 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    else:
        df[col] = 0

# -------------------------------------------------------
# 3️⃣ Compute Totals and Rankings
# -------------------------------------------------------
df["total_payment"] = df["q2_achievement"] + df["monthly_payment_q2"] + df["benefit_gain"] + df["fee_charge"] - df["expenditure"]
df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)

# -------------------------------------------------------
# 4️⃣ Display Member Data
# -------------------------------------------------------
st.subheader("📋 Member Payment Overview")
st.dataframe(df, use_container_width=True)
st.info(f"Total Members: **{df['name'].nunique()}** | Total Rows: **{df.shape[0]}**")

# -------------------------------------------------------
# 5️⃣ Update Monthly Payment
# -------------------------------------------------------
st.subheader("💵 Update Monthly Payment (Q2)")
col1, col2 = st.columns(2)
with col1:
    member_name = st.selectbox("Select Member", df["name"])
with col2:
    added_payment = st.number_input("Enter Payment Amount to Add (ETB)", min_value=0, step=100)

if st.button("✅ Update Payment"):
    df.loc[df["name"] == member_name, "monthly_payment_q2"] += added_payment
    df["total_payment"] = df["q2_achievement"] + df["monthly_payment_q2"] + df["benefit_gain"] + df["fee_charge"] - df["expenditure"]
    df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)
    st.success(f"Payment for **{member_name}** updated successfully!")

# -------------------------------------------------------
# 6️⃣ Plan vs Achievement Analysis
# -------------------------------------------------------
st.subheader("📈 Plan vs Achievement Analysis")
df["difference_q1"] = df["q1_achievement"] - df["q1_plan"]
df["difference_q2"] = df["q2_achievement"] - df["q2_plan"]

analysis_cols = ["name", "q1_plan", "q1_achievement", "difference_q1",
                 "q2_plan", "q2_achievement", "difference_q2",
                 "fee_charge", "voluntary_saving", "monthly_payment_q2",
                 "benefit_gain", "expenditure", "total_payment", "payment_rank"]
st.dataframe(df[analysis_cols], use_container_width=True)

# -------------------------------------------------------
# 7️⃣ Summary Metrics
# -------------------------------------------------------
st.subheader("📊 Summary Metrics")
Q1_plan = df["q1_plan"].sum()
Q1_achievement = df["q1_achievement"].sum()
Q2_plan = df["q2_plan"].sum()
Q2_achievement = df["q2_achievement"].sum()
T_monthly = df["monthly_payment_q2"].sum()
T_fee = df["fee_charge"].sum()
T_voluntary = df["voluntary_saving"].sum()
T_benefit = df["benefit_gain"].sum()
T_expenditure = df["expenditure"].sum()
G_total = (df["q2_achievement"] + df["benefit_gain"] + df["fee_charge"] + df["monthly_payment_q2"] - df["expenditure"]).sum()

cols = st.columns(9)
cols[0].metric("Q1 Plan", f"{Q1_plan:,.0f}")
cols[1].metric("Q1 Achievement", f"{Q1_achievement:,.0f}", delta=int(Q1_achievement - Q1_plan))
cols[2].metric("Q2 Plan", f"{Q2_plan:,.0f}")
cols[3].metric("Q2 Achievement", f"{Q2_achievement:,.0f}", delta=int(Q2_achievement - Q2_plan))
cols[4].metric("Q2 Monthly Payment", f"{T_monthly:,.0f}")
cols[5].metric("Fee Charge", f"{T_fee:,.0f}")
cols[6].metric("Voluntary Saving", f"{T_voluntary:,.0f}")
cols[7].metric("Benefit Gain", f"{T_benefit:,.0f}")
cols[8].metric("Expenditure", f"{T_expenditure:,.0f}")

st.markdown(f"### 💰 **Grand Total Payment: {G_total:,.2f} ETB**")

# -------------------------------------------------------
# 8️⃣ Visualization of Totals
# -------------------------------------------------------
st.subheader("📊 Visualization of Totals")
totals = {
    "Q1 Plan": Q1_plan,
    "Q1 Achievement": Q1_achievement,
    "Q2 Plan": Q2_plan,
    "Q2 Achievement": Q2_achievement,
    "Monthly Payment Q2": T_monthly,
    "Fee Charge": T_fee,
    "Voluntary Saving": T_voluntary,
    "Benefit Gain": T_benefit,
    "Expenditure": T_expenditure,
    "Grand Total": G_total
}

# Bar Chart
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(totals.keys(), totals.values(),
       color=['skyblue', 'green', 'orange', 'purple', 'red', 'pink', 'gray', 'gold', 'teal', 'navy'])
ax.set_ylabel("Amount (ETB)")
ax.set_title("EGSA 2025 Totals Overview")
for i, v in enumerate(totals.values()):
    ax.text(i, v + max(totals.values())*0.01, f"{v:,.0f}", ha='center')
st.pyplot(fig)

# Pie Chart
fig2, ax2 = plt.subplots(figsize=(7, 7))
ax2.pie(totals.values(), labels=totals.keys(), autopct='%1.1f%%', startangle=140,
        colors=['skyblue', 'green', 'orange', 'purple', 'red', 'pink', 'gray', 'gold', 'teal', 'navy'])
ax2.axis('equal')
st.pyplot(fig2)

# -------------------------------------------------------
# 9️⃣ Add TOTAL Row for Final Report
# -------------------------------------------------------
total_row = pd.DataFrame({
    "name": ["🟩 TOTAL 🟩"],
    "q1_plan": [Q1_plan],
    "q1_achievement": [Q1_achievement],
    "monthly_payment_q2": [T_monthly],
    "q2_plan": [Q2_plan],
    "q2_achievement": [Q2_achievement],
    "fee_charge": [T_fee],
    "voluntary_saving": [T_voluntary],
    "benefit_gain": [T_benefit],
    "expenditure": [T_expenditure],
    "total_payment": [G_total],
    "payment_rank": [None],
    "difference_q1": [Q1_achievement - Q1_plan],
    "difference_q2": [Q2_achievement - Q2_plan]
})
final_df = pd.concat([df, total_row], ignore_index=True)
st.subheader("📗 Final Report with TOTAL Row")
st.dataframe(final_df, use_container_width=True)

# -------------------------------------------------------
# 🔟 Download Updated Data
# -------------------------------------------------------
st.subheader("💾 Save or Download Updated Data")
buffer = BytesIO()
final_df.to_excel(buffer, index=False, engine='openpyxl')
buffer.seek(0)

st.download_button(
    label="💾 Download Updated Excel File",
    data=buffer,
    file_name="EGSA2025_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
