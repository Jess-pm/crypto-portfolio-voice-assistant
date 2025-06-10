# 🙋‍♀️ About the Author
This project was developed as part of my portfolio to demonstrate proficiency in hands-on ML integration, product-centric design, and rapid prototyping to bridge the gap between strategy and working implementation.

# 🗣️ Crypto Portfolio Voice Assistant
This project demonstrates a fully working voice-based assistant that allows users to save and retrieve their crypto portfolio by speaking naturally — powered by LangChain, Flask and OpenAI GPT models. Designed with real-time voice interaction, multi-turn state handling, and live price lookups, it showcases the integration of language models with backend logic to deliver AI-enabled user flows.

## 📌 Project Highlights
- Built a natural language voice interface to track and query crypto holdings
- Integrated LangChain + OpenAI GPT for parsing user intents and content
- Designed multi-turn voice flow to:
  - Save multiple coins (e.g. "2 Ethereum", "0.5 Bitcoin")
  - Confirm each input with the user
  - Respond with total portfolio value + % breakdown
- Used Flask for the backend and Web Speech API in browser for voice input/output
- Fetched real-time coin prices using CoinGecko API
- Stored session and portfolio data using custom Python logic + JSON files

🎯 Product Thinking
🔄 Natural interaction loop: showcases how AI assistants can support hands-free workflows
🧱 Modular backend: clear separation of LLM logic, pricing, session state
🧪 Testable architecture: state saved in JSON, no external DB needed
🚀 Rapid prototyping: used production-ready libraries like Flask + LangChain to demonstrate viability

## 🧠 User Flow
1. User starts the assistant (via browser UI)
2. Prompt: “Do you want to know the value of your saved portfolio or do you want to save a new portfolio?”
3. If saving: user speaks coins and quantities (e.g. “3 Bitcoin”, “2 Ethereum”)
4. Assistant confirms each coin aloud before saving
5. When user says “done”, assistant calculates:
   - 💰 Total USD value
   - 📊 Percentage by coin
6. If querying: assistant returns the last saved portfolio breakdown

## 🗂️ Tech Stack Overview
| Layer | Technology |
|-------|------------|
| 🔮 LLM | langchain, langchain-openai, openai |
| 🧠 Logic | Python custom state tracker (session_store.py, save_flow.py) |
| 🌐 Backend | Flask web framework |
| 🧾 Voice UI | HTML + JS (Web Speech API), rendered via templates/index.html |
| 📉 Price Data | CoinGecko API (via price_fetcher.py) |
| 🗂️ Persistence | user_portfolio.json (file-based storage for simplicity) |

## 🛠️ Implementation Details
### 🔄 Intent Parsing with LangChain
- Used LangChain's OpenAI wrapper to interpret user intent (agent.py)
- Prompts determine whether user is saving or querying portfolio
- Parsed free-text into structured coin+quantity via custom portfolio_parser.py

### 🧠 Stateful Session Flow
- Each user interaction is tracked across turns using session_store.py
- Coins confirmed one at a time, saved into memory
- Final summary only returned after “done” is detected

### 🧪 Price Fetching
- Live USD prices retrieved via CoinGecko API
- Used to calculate:
  - Total USD value
  - Percentage breakdown by coin

### 🔊 Voice Interface
- Voice input via Web Speech API (browser-based)
- Voice responses generated via JavaScript speech synthesis
- UI built in index.html and rendered via Flask

