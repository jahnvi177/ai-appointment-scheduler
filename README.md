# 📅 AI Appointment Scheduler (Google Calendar + Langchain + FastAPI)

This project is a conversational AI agent that helps users schedule appointments by:
- Understanding natural language like "next Friday at 10am"
- Checking availability in your Google Calendar
- Suggesting open time slots dynamically
- Booking confirmed events via chat

---

## 🚀 Tech Stack

- Python 3.11
- FastAPI (backend)
- Streamlit (frontend chat UI)
- Google Calendar API
- LangChain + OpenAI LLM
- Docker / Docker Compose (for local deployment)

---


---

## 🪟 Setup on Windows 11

### Step 1: 🐳 Install Docker Desktop
- [Install Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- Enable WSL2 during installation if prompted

---

### Step 2: 🔐 Google Calendar Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a Service Account and enable the **Google Calendar API**
3. Download the JSON credentials file
4. Save it as: `app/credentials.json`
5. Share your calendar with the service account email

---

### Step 3: 📦 Build and Run the App

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
