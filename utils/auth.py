import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import base64
import os

class Auth:
    def __init__(self, json_url, token, session_days=1, local_file="users_local.json"):
        self.json_url = json_url
        self.token = token
        self.session_days = session_days
        self.local_file = local_file  # ✅ Local fallback file

    def fetch_users(self):
        """Fetch users from GitHub first; if it fails, use local file."""
        headers = {"Authorization": f"token {self.token}"} if self.token else {}
        try:
            r = requests.get(self.json_url, headers=headers, timeout=10)
            r.raise_for_status()
            response_data = r.json()
            if "content" in response_data:
                data = json.loads(base64.b64decode(response_data["content"]).decode())
            else:
                data = response_data
            return data
        except Exception as e:
            st.warning(f"⚠️ Remote user list failed, using local file. ({e})")
            if os.path.exists(self.local_file):
                with open(self.local_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            st.error("❌ Local fallback file not found.")
            return []

    def login(self):
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        username = st.text_input("Username")
        key = st.text_input("Production Key", type="password")

        if st.button("Login"):
            users = self.fetch_users()
            for user in users:
                if user["username"] == username and user["production_key"] == key:
                    if not user.get("active", True):
                        st.error("❌ User disabled by admin")
                        return False
                    if datetime.now().date() > datetime.fromisoformat(user["expiration_date"]).date():
                        st.error("❌ Key expired")
                        return False
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user
                    st.session_state["expiry"] = datetime.now() + timedelta(days=self.session_days)
                    st.success(f"✅ Welcome {username}")
                    return True
            st.error("❌ Invalid username or key")
        return st.session_state["logged_in"]

    def session_valid(self):
        return (
            st.session_state.get("logged_in", False)
            and datetime.now() < st.session_state.get("expiry", datetime.now())
        )
