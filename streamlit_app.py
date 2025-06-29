"""
Streamlit chat UI for AI appointment scheduler.
Now includes robust error handling and smoother fallback behavior.
"""
import os
import streamlit as st
import requests
# Endpoint defined via Docker Compose env var
API_HOST = os.getenv("API_HOST", "http://localhost:8000")
st.title("📅 AI Appointment Scheduler")

# Message persistence
if "messages" not in st.session_state: st.session_state.messages = []

# Show chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# Handle new user input
user_input = st.chat_input("Schedule an appointment...")
# Displays an interactive chat input box at the bottom of the screen and captures user queries
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
         # Renders the assistant’s reply as a chat bubble inside the Streamlit app
      try: 
            response = requests.post(f"{API_HOST}/chat", json={"message": user_input})
            # Sends the user message to the FastAPI backend and retrieves the AI-generated response
            if response.ok:
                reply = response.json().get("reply", "⚠️ No reply received.")
            else:
                reply = f"⚠️ Server error: {response.status_code}"
      except Exception as e:
            reply = "⚠️ Sorry, I couldn't reach the server. Please try again later."
      st.markdown(reply)
      st.session_state.messages.append({"role": "assistant", "content": reply})
