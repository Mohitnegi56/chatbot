# 🤖 LangGraph AI Chatbot

A multi-threaded AI chatbot built using **LangGraph**, **LangChain**, **HuggingFace**, **SQLite**, and **Streamlit**.

🔗 **Live App:**  
👉 https://chatbot-cqhq4vpuraen6vxo4g4nt4.streamlit.app/

---

## 🚀 Features

- 🔄 Multi-thread conversations
- 💾 Persistent memory using SQLite
- 🧠 LangGraph orchestration engine
- 🤗 HuggingFace LLM integration
- ⚡ Streaming responses
- 🎨 Modern gradient + glassmorphism UI by taking help from chatgpt
- 🗑 Delete conversations
- 🕒 Message timestamps
- 💬 Markdown & code block rendering
- ☁ Deployed on Streamlit Cloud

---

## 🏗 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend Logic | LangGraph |
| LLM Provider | HuggingFace Inference API |
| LLM Framework | LangChain |
| Database | SQLite |
| Deployment | Streamlit Cloud |

---

## 📂 Project Structure
├── backend.py # LangGraph + SQLite backend
├── frontend.py # Streamlit user interface
├── requirements.txt # Python dependencies
└── README.md # Documentation

---

## ⚙️ Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Mohitnegi56/chatbot.git
cd chatbot
pip install -r requirements.txt
Create .env file: Add huggingface token
HUGGINGFACEHUB_API_TOKEN=your_token_here
streamlit run frontend.py
```

###🧠 How It Works

User sends message via Streamlit UI
Message enters LangGraph workflow
HuggingFace model generates response
Response streams back to UI
Conversation state stored in SQLite
Threads restored using persistent checkpoint

###📈 Why This Project Matters

This project demonstrates:
LLM orchestration with LangGraph
Persistent memory systems
Multi-thread chat handling
Real-world AI app deployment
Production-level architecture practices

###🔐 Security

API keys stored securely in Streamlit Secrets
.env and database files are excluded via .gitignore
No secrets committed to GitHub

###👨‍💻 Author

Mohit Negi
AI/ML Developer | NLP Enthusiast

---

⭐ If you found this project interesting, consider giving it a star!
