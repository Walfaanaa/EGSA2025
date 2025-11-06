# =======================================================
# 🏦 EGSA 2025 Management System (Cloud + Secure Version)
# =======================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO

# -------------------------------------------------------
# 🔐 Simple Password Gate
# -------------------------------------------------------
st.set_page_config(page_title="EGSA 2025 Management System", layout="wide")

PASSWORD = "EGSA2025!"  # ✅ change this to your own password

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
# 1️⃣ Page Setup (Centered Rotating Logo)
# -------------------------------------------------------
logo_path = "EGSA.png"  # ✅ file in same repo or assets folder
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
file_path = "EGSA2025_info.xlsx"  # ✅ Excel file in repo root
if not os.path.exists(file_path):
    st.error("❌ Excel file not found! Please ensure 'EGSA2025_info.xlsx' is uploaded.")
    st.stop()

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df["Name"] = df["Name"].astype(str).str.strip()

# 🧹 Remove TOTAL row(s) & duplicates
df = df[~df["Name"].str.contains("TOTAL", case=False, na=False)]
df = df.drop_duplicates()

# 🧮 Clean numeric columns
numeric_cols = ["Q1_plan", "Q1_achievement", "Monthly_payment_Q2", "Q2_plan", 
                "fee_charge", "volentary_saving", "Benefit_gain", "Expenditure"]
for col in numeric_cols:
    if col not in df.columns:
        df[col] = 0
    df[col] = df[col].astype(str).str.replace(",", "").str.strip()
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -------------------------------------------------------
# 3️⃣ Compute Totals and Rankings (Updated SQL Logic)
# -------------------------------------------------------
df["total_payment"] = df["Q1_achievement"] + df["Monthly_payment_Q2"] + df["volentary_saving"] + df["fee_charge"]
df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)

# -------------------------------------------------------
# 4️⃣ Display Member Data
# -------------------------------------------------------
st.subheader("📋 Member Payment Overview")
st.dataframe(df, use_container_width=True)
st.info(f"Total Members: **{df['Name'].nunique()}** | Total Rows: **{df.shape[0]}**")

# -------------------------------------------------------
# 5️⃣ Update Monthly Payment
# -------------------------------------------------------
st.subheader("💵 Update Monthly Payment (Q2)")
col1, col2 = st.columns(2)

with col1:
    member_name = st.selectbox("Select Member", df["Name"])
with col2:
    added_payment = st.number_input("Enter Payment Amount to Add (ETB)", min_value=0, step=100)

if st.button("✅ Update Payment"):
    df.loc[df["Name"] == member_name, "Monthly_payment_Q2"] += added_payment
    df["total_payment"] = df["Q1_achievement"] + df["Monthly_payment_Q2"] + df["volentary_saving"] + df["fee_charge"]
    df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)
    st.success(f"Payment for **{member_name}** updated successfully!")

# -------------------------------------------------------
# 6️⃣ Plan vs Achievement Analysis
# -------------------------------------------------------
st.subheader("📈 Plan vs Achievement Analysis")
df["Difference_Q1"] = df["Q1_achievement"] - df["Q1_plan"]
analysis_cols = ["Name", "Q1_plan", "Q1_achievement", "Difference_Q1",
                 "fee_charge", "volentary_saving", "Monthly_payment_Q2",
                 "Benefit_gain", "Expenditure", "total_payment", "payment_rank"]
st.dataframe(df[analysis_cols], use_container_width=True)

# -------------------------------------------------------
# 7️⃣ Summary Metrics (Updated)
# -------------------------------------------------------
st.subheader("📊 Summary Metrics")

total_plan = df["Q1_plan"].sum()
total_achievement = df["Q1_achievement"].sum()
total_monthly = df["Monthly_payment_Q2"].sum()
total_fee = df["fee_charge"].sum()
total_voluntary = df["volentary_saving"].sum()
total_benefit = df["Benefit_gain"].sum()       # ✅ Added
total_expenditure = df["Expenditure"].sum()    # ✅ Added
grand_total = df["total_payment"].sum()+df["Benefit_gain"] - df["Expenditure"]

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)  # ✅ add extra columns
col1.metric("Q1 Plan", f"{total_plan:,.0f}")
col2.metric("Q1 Achievement", f"{total_achievement:,.0f}", delta=int(total_achievement - total_plan))
col3.metric("Q2 Monthly Payment", f"{total_monthly:,.0f}")
col4.metric("Fee Charge", f"{total_fee:,.0f}")
col5.metric("Voluntary Saving", f"{total_voluntary:,.0f}")
col6.metric("Benefit Gain", f"{total_benefit:,.0f}")        # ✅ new metric
col7.metric("Expenditure", f"{total_expenditure:,.0f}")      # ✅ new metric

st.markdown(f"### 💰 **Grand Total Payment: {grand_total:,.2f} ETB**")

# -------------------------------------------------------
# 8️⃣ Visualization of Totals
# -------------------------------------------------------
st.subheader("📊 Visualization of Totals")
totals = {
    "Q1 Plan": total_plan,
    "Achievement": total_achievement,
    "Monthly Payment Q2": total_monthly,
    "Fee Charge": total_fee,
    "Voluntary Saving": total_voluntary,
    "Benefit Gain": total_benefit,
    "Expenditure": total_expenditure,
    "Total Payment": grand_total
}

# --- Bar Chart ---
st.write("### 📊 Bar Chart")
fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(totals.keys(), totals.values(), color=['skyblue', 'green', 'orange', 'purple', 'red', 'pink', 'gray', 'gold'])
ax.set_ylabel("Amount (ETB)")
ax.set_title("EGSA 2025 Totals Overview")
for i, v in enumerate(totals.values()):
    ax.text(i, v + max(totals.values()) * 0.01, f"{v:,.0f}", ha='center')
st.pyplot(fig)

# --- Pie Chart ---
st.write("### 🥧 Pie Chart")
fig2, ax2 = plt.subplots(figsize=(7, 7))
ax2.pie(totals.values(), labels=totals.keys(), autopct='%1.1f%%', startangle=140,
        colors=['skyblue', 'green', 'orange', 'purple', 'red', 'pink', 'gray', 'gold'])
ax2.axis('equal')
st.pyplot(fig2)

# -------------------------------------------------------
# 9️⃣ Add TOTAL Row for Final Report
# -------------------------------------------------------
total_row = pd.DataFrame({
    "Name": ["🟩 TOTAL 🟩"],
    "Q1_plan": [total_plan],
    "Q1_achievement": [total_achievement],
    "Monthly_payment_Q2": [total_monthly],
    "Q2_plan": [df["Q2_plan"].sum()],
    "fee_charge": [total_fee],
    "volentary_saving": [total_voluntary],
    "Benefit_gain": [total_benefit],
    "Expenditure": [total_expenditure],
    "total_payment": [grand_total],
    "payment_rank": [None]
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



