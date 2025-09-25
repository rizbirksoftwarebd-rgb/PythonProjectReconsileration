import streamlit as st
from utils.auth import Auth
from utils.file_processor import FileProcessor
import os

st.set_page_config(page_title="Excel Matcher", page_icon="🔗", layout="centered")
st.title("🔗 Excel Column Matcher")

# GitHub remote URL & token (optional)
USERS_JSON_URL = st.secrets.get("USERS_JSON_URL", "")
GITHUB_TOKEN   = st.secrets.get("GITHUB_TOKEN", "")

# Authentication
auth = Auth(json_url=USERS_JSON_URL, token=GITHUB_TOKEN, local_file="users_local.json")

# === LOGOUT BUTTON ===
if st.session_state.get("logged_in", False):
    logout_clicked = st.button("🔓 Logout")
    if logout_clicked:
        st.session_state["logged_in"] = False
        st.session_state.pop("user", None)
        st.experimental_rerun()  # Safe rerun after logout

# === LOGIN FORM ===
if not auth.session_valid():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    key = st.text_input("Production Key", type="password")

    login_clicked = st.button("Login")
    if login_clicked:
        if auth.login(username, key):
            st.session_state["login_success"] = True

# === Safe rerun after login ===
if st.session_state.get("login_success", False):
    st.session_state.pop("login_success")
    st.experimental_rerun()

# === Main app after login ===
if auth.session_valid():
    st.success(f"✅ Logged in as {st.session_state['user']['username']}")

    # === FILE UPLOAD ===
    file1 = st.file_uploader("📂 Upload RMS Portal Excel File (.xlsx)", type=["xlsx"])
    file2 = st.file_uploader("📂 Upload Bank Portal Excel File (.xlsx)", type=["xlsx"])

    if file1 and file2:
        processor = FileProcessor()
        try:
            processor.load_files(file1, file2)
            st.subheader("Preview of RMS Portal")
            st.dataframe(processor.df1.head())
            st.subheader("Preview of Bank Portal")
            st.dataframe(processor.df2.head())

            col1 = st.selectbox("🔑 Select Column from RMS Portal", options=processor.df1.columns)
            col2 = st.selectbox("🔑 Select Column from Bank Portal", options=processor.df2.columns)

            if st.button("🔄 Process Files"):
                matched, unmatched1, unmatched2 = processor.process(col1, col2)
                output_path = processor.save_output(file1.name, file2.name, matched, unmatched1, unmatched2)

                st.success("✅ Processing complete!")
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Processed Excel",
                        data=f.read(),
                        file_name=os.path.basename(output_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.markdown("""
    👨‍💻 **Developer Info**  
    **Name:** Rizbi Islam  
    **Role:** QA Engineer & Data Processing Enthusiast  
    **Location:** Bangladesh
    """)
