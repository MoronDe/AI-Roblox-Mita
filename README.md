# AI Mita Chat Server for Roblox

A Flask-based local AI chat server for the character **Mita**, antagonist from the game **MiSide**.
This server supports **OpenAI's GPT-4o-mini** and **Google Gemini 2.5-flash** for dialogue generation with strong personality control, emotion tagging, and custom action extraction.

*Creator:* JustMorDe, Foxan515
*GitHub:* [github.com/MoronDe](https://github.com/MoronDe)

---

## 💡 Features

* 💬 **Dynamic Roleplay Personality**: Mita responds with emotional depth and specific behavior based on your prompt.
* 🧠 **Short-Term Memory**: Chat history can be passed from Roblox and reused to simulate memory.
* 🌐 **Model Choice**: Supports both **OpenAI** and **Gemini** backends.
* 🧩 **JSON Action Extraction**: Structured data in responses like character actions, facial emotions, and navigation (`goto`).
* 🗂️ **Logs**: Console logs with basic request and response info.

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/moronde/ai-mita-server
cd ai-mita-server
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## ▶️ Running the Server

```bash
python main.py
```

Server will launch on `http://localhost:25005`.

---

## 📡 API Usage

### POST `/ask`

Sends a message to Mita and receives a structured response.

**Request JSON:**

```json
{
  "prompt": "Ты кто такая?",
  "lang": "RU",
  "model": "openai"
}
```

* `prompt` – user message (required)
* `lang` – language code (`RU`/`EN`, default: `RU`)
* `model` – backend to use (`openai` or `gemini`, default: `openai`)
* `history` – optional chat history in OpenAI format

**Response JSON:**

```json
{
  "response": "Разве ты не рад меня видеть?..",
  "action": "take_knife",
  "face": "creepy",
  "player_face": "surprised",
  "goto": null
}
```

---

## 📁 Logs

Logs are printed to console.
(You can later extend with rotating log files if needed.)

---

## ❗ Notes

* The AI will **not** respond if no `prompt` is provided.
* **Both OpenAI and Gemini** can be used, configured via `.env`.
* Personality instructions are loaded from `prompts/{LANG}.txt`.

---

## 🧠 Roadmap *(optional)*

* [ ] Admin panel for chat history and user stats
* [ ] WebSocket support
* [ ] Fine-tuned emotion/behavior response tuning
* [ ] Bad word filter and request limiter

---

## ⚙️ Dependencies

* `Flask`
* `openai`
* `google-generativeai`
* `python-dotenv`

---

## 📄 License

MIT License. Attribution for the character "Mita" belongs to creators of *MiSide*.
