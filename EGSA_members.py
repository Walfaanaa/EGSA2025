# =======================================================
# 🏦 EGSA 2025 Management System (Updated with SQL Logic)
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

PASSWORD = "EGSA2025!"

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
# ✅ Logo
# -------------------------------------------------------
logo_path = "EGSA.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
else:
    st.error("❌ Logo file missing!")
    st.stop()

st.markdown(f"""
<div style="text-align:center;">
    <img src="data:image/png;base64,{logo_data}" width="200">
    <h1 style="color:#2c3e50;">EGSA 2025 Management System</h1>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# ✅ Load & Clean Data
# -------------------------------------------------------
file_path = "EGSA2025_info.xlsx"
if not os.path.exists(file_path):
    st.error("❌ Excel file not found!")
    st.stop()

df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df["Name"] = df["Name"].astype(str).str.strip()

# Remove TOTAL rows
df = df[~df["Name"].str.contains("TOTAL", case=False, na=False)]

# Ensure numeric fields exist
numeric_cols = [
    "Q1_plan", "Q1_achievement", "Monthly_payment_Q2", "Q2_plan",
    "fee_charge", "volentary_saving", "Benefit_gain", "Expenditure"
]

for col in numeric_cols:
    if col not in df.columns:
        df[col] = 0
    df[col] = (
        df[col].astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# -------------------------------------------------------
# ✅ Compute TOTAL PAYMENT (SQL Logic)
# -------------------------------------------------------
df["total_payment"] = (
    df["Q1_achievement"]
    + df["Monthly_payment_Q2"]
    + df["volentary_saving"]
    + df["fee_charge"]
    + df["Benefit_gain"]
    - df["Expenditure"]
)

# ✅ Rank based on SQL logic (dense)
df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)

# -------------------------------------------------------
# ✅ Display Data
# -------------------------------------------------------
st.subheader("📋 Member Payment Overview (SQL Logic Applied)")
st.dataframe(df, use_container_width=True)

# -------------------------------------------------------
# ✅ Update Monthly Payment
# -------------------------------------------------------
st.subheader("💵 Update Monthly Payment (Q2)")

col1, col2 = st.columns(2)
with col1:
    member_name = st.selectbox("Select Member", df["Name"])
with col2:
    added_payment = st.number_input("Enter Payment Amount to Add", min_value=0, step=50)

if st.button("✅ Update Payment"):
    df.loc[df["Name"] == member_name, "Monthly_payment_Q2"] += added_payment

    # Recalculate totals
    df["total_payment"] = (
        df["Q1_achievement"]
        + df["Monthly_payment_Q2"]
        + df["volentary_saving"]
        + df["fee_charge"]
        + df["Benefit_gain"]
        - df["Expenditure"]
    )
    df["payment_rank"] = df["total_payment"].rank(method="dense", ascending=False).astype(int)

    st.success(f"✅ Updated payment for {member_name}")

# -------------------------------------------------------
# ✅ Summary Metrics
# -------------------------------------------------------
st.subheader("📊 Summary Metrics")

total_row_values = {
    "Q1_plan": df["Q1_plan"].sum(),
    "Q1_achievement": df["Q1_achievement"].sum(),
    "Monthly_payment_Q2": df["Monthly_payment_Q2"].sum(),
    "Q2_plan": df["Q2_plan"].sum(),
    "fee_charge": df["fee_charge"].sum(),
    "volentary_saving": df["volentary_saving"].sum(),
    "Benefit_gain": df["Benefit_gain"].sum(),
    "Expenditure": df["Expenditure"].sum(),
    "total_payment": df["total_payment"].sum()
}

# -------------------------------------------------------
# ✅ Add FINAL TOTAL Row (MATCHES YOUR SQL)
# -------------------------------------------------------
total_row = pd.DataFrame({
    "Name": ["🟩 TOTAL 🟩"],
    "Q1_plan": [total_row_values["Q1_plan"]],
    "Q1_achievement": [total_row_values["Q1_achievement"]],
    "Monthly_payment_Q2": [total_row_values["Monthly_payment_Q2"]],
    "Q2_plan": [total_row_values["Q2_plan"]],
    "fee_charge": [total_row_values["fee_charge"]],
    "volentary_saving": [total_row_values["volentary_saving"]],
    "Benefit_gain": [total_row_values["Benefit_gain"]],
    "Expenditure": [total_row_values["Expenditure"]],
    "total_payment": [total_row_values["total_payment"]],
    "payment_rank": [None]
})

final_df = pd.concat([df, total_row], ignore_index=True)

st.subheader("📗 Final Report with SQL TOTAL Row")
st.dataframe(final_df, use_container_width=True)

# -------------------------------------------------------
# ✅ Download Updated File
# -------------------------------------------------------
buffer = BytesIO()
final_df.to_excel(buffer, index=False, engine="openpyxl")
buffer.seek(0)

st.download_button(
    label="💾 Download Updated Excel File",
    data=buffer,
    file_name="EGSA2025_updated.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
