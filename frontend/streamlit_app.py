import streamlit as st
import requests
from datetime import datetime

# -------------------------------
# Configuration
# -------------------------------
# Point this at your deployed FastAPI URL:
BACKEND_URL = "https://<your-backend-domain>.onrender.com"  # e.g. https://calendarbookingbot.onrender.com

st.set_page_config(page_title="📅 Calendar Assistant", layout="centered")

# -------------------------------
# Header
# -------------------------------
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>💬 Talk to Your Calendar Assistant</h1>
        <p style="color: gray;">Book, cancel, or view calendar meetings with natural language.</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# Session State
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# Clear chat history
# -------------------------------
with st.sidebar:
    st.markdown("### 🧹 Reset Chat")
    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

# -------------------------------
# Chat input
# -------------------------------
user_input = st.chat_input("Ask me anything about your calendar...")

# -------------------------------
# Send to FastAPI
# -------------------------------
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("🤖 Thinking..."):
        try:
            resp = requests.post(f"https://calendarbookingbot-backend.streamlit.app/chat", json={"message": user_input})
            reply = resp.json().get("response", "⚠️ No response from server.")
        except Exception as e:
            reply = f"❌ Error: {str(e)}"
    st.session_state.chat_history.append(("bot", reply))

# -------------------------------
# Display chat history
# -------------------------------
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)
