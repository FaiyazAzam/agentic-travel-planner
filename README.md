# 🧭 Agentic Travel Planner

This project is an AI-powered travel planning assistant. It uses an **agentic workflow**, a **local vector database (FAISS)**, and a **Streamlit-based UI** to generate detailed travel itineraries based on user inputs like **destination**, **travel dates**, **interests**, and **budget**.

---

## 🚀 Features

- 🧠 **Agentic AI workflow** with tool usage
- 🔍 **Retrieval-Augmented Generation (RAG)** via FAISS-based local knowledge
- 📅 **Personalized itineraries** based on dynamic user input
- 💻 **Streamlit UI** frontend for a smooth experience
- 🌍 Works offline with local city datasets under `/data`

---

## 📁 Folder Structure
Agentic_AI/
│
├── data/ # Local city knowledgebase (Milan, Tokyo, etc.)
├── .env # API keys & environment config
├── build_vector_store.py # Builds FAISS vector store from data
├── sample_db_creation.py # Initializes sample RAG database
├── travel_agent_task.py # Core agentic planning logic
├── travel_plan_utils.py # Utilities for plan formatting and structure
├── travel_requirements.txt # Text file of required user input fields
├── planner_app.py # Streamlit UI runner
├── requirements.txt # Python dependencies
└── README.md # You’re here!