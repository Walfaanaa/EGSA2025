# --- Encode local logo as Base64 ---
logo_path = r"C:\Users\User\Downloads\EGSA.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = f.read()
        logo_base64 = base64.b64encode(logo_data).decode()
else:
    st.error("❌ Logo file not found! Please check the path.")
    st.stop()
