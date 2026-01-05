# =======================================================
# 🏦 EGSA 2025 Management System – Q2 Focused
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
st.set_page_config(page_title="EGSA 2025 Q2 Management System", layout="wide")
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
    <img src="data:image/png;base64,{logo_base64}" width="200">
    <h1 style="color:#2c3e50;">EGSA 2025 Q2 Management System</h1>
    <div style="color:gray;font-size:1.1em;">Q2 Payment and Performance Tracking</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# 2️⃣ Load & Clean Data
# -------------------------------------------------------
file_path = "EGSA2025_Q2.xlsx"  # Replace with your file
if not os.path.exists(file_path):
    st.error("❌ Excel file not found! Please upload the Q2 file.")
    st.stop()

df = pd.read_excel(file_path)

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df["name"] = df["name"].astype(str).str.strip()

# Remove TOTAL rows and duplicates
df = df[~df["name"].str.contains("TOTAL", case=False, na=False)]
df = df.drop_duplicates()

# Clean numeric columns
numeric_cols = ["monthly_payment_q2", "q2_plan", "q2_achievement", "fee_charge", "benefit_gain"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -------------------------------------------------------
# 3️⃣ Compute Total Payment, Difference, and Rankings
# -------------------------------------------------------
df["total_payment"] = df["q2_achievement"] + df["monthly_payment_q2"] + df["fee_charge"] + df["benefit_gain"]
df["difference_q2"] = df["q2_achievement"] - df["q2_plan"]
df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)

# -------------------------------------------------------
# 4️⃣ Display Member Data
# -------------------------------------------------------
st.subheader("📋 Q2 Payment Overview")
st.dataframe(df, use_container_width=True)

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
    df["total_payment"] = df["q2_achievement"] + df["monthly_payment_q2"] + df["fee_charge"] + df["benefit_gain"]
    df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)
    st.success(f"Payment for **{member_name}** updated successfully!")

# -------------------------------------------------------
# 6️⃣ Summary Metrics
# -------------------------------------------------------
st.subheader("📊 Summary Metrics")
Q2_plan = df["q2_plan"].sum()
Q2_achievement = df["q2_achievement"].sum()
T_monthly = df["monthly_payment_q2"].sum()
T_fee = df["fee_charge"].sum()
T_benefit = df["benefit_gain"].sum()
G_total = df["total_payment"].sum()

cols = st.columns(6)
cols[0].metric("Q2 Plan", f"{Q2_plan:,.0f}")
cols[1].metric("Q2 Achievement", f"{Q2_achievement:,.0f}", delta=int(Q2_achievement - Q2_plan))
cols[2].metric("Monthly Payment Q2", f"{T_monthly:,.0f}")
cols[3].metric("Fee Charge", f"{T_fee:,.0f}")
cols[4].metric("Benefit Gain", f"{T_benefit:,.0f}")
cols[5].metric("Grand Total Payment", f"{G_total:,.0f}")

# -------------------------------------------------------
# 7️⃣ Visualization
# -------------------------------------------------------
st.subheader("📊 Visualization of Totals")
totals = {
    "Q2 Plan": Q2_plan,
    "Q2 Achievement": Q2_achievement,
    "Monthly Payment": T_monthly,
    "Fee Charge": T_fee,
    "Benefit Gain": T_benefit,
    "Grand Total": G_total
}

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(totals.keys(), totals.values(), color=['orange', 'purple', 'red', 'pink', 'gold', 'teal'])
ax.set_ylabel("Amount (ETB)")
ax.set_title("EGSA 2025 Q2 Totals Overview")
for i, v in enumerate(totals.values()):
    ax.text(i, v + max(totals.values())*0.01, f"{v:,.0f}", ha='center')
st.pyplot(fig)

# Pie Chart
fig2, ax2 = plt.subplots(figsize=(7, 7))
ax2.pie(totals.values(), labels=totals.keys(), autopct='%1.1f%%', startangle=140,
        colors=['orange', 'purple', 'red', 'pink', 'gold', 'teal'])
ax2.axis('equal')
st.pyplot(fig2)

# -------------------------------------------------------
# 8️⃣ Add TOTAL Row & Download
# -------------------------------------------------------
total_row = pd.DataFrame({
    "name": ["🟩 TOTAL 🟩"],
    "monthly_payment_q2": [T_monthly],
    "q2_plan": [Q2_plan],
    "q2_achievement": [Q2_achievement],
    "fee_charge": [T_fee],
    "benefit_gain": [T_benefit],
    "total_payment": [G_total],
    "difference_q2": [Q2_achievement - Q2_plan],
    "payment_rank": [None]
})
final_df = pd.concat([df, total_row], ignore_index=True)
st.subheader("📗 Final Report with TOTAL Row")
st.dataframe(final_df, use_container_width=True)

buffer = BytesIO()
final_df.to_excel(buffer, index=False, engine='openpyxl')
buffer.seek(0)
st.download_button(
    label="💾 Download Updated Excel File",
    data=buffer,
    file_name="EGSA2025_Q2_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
