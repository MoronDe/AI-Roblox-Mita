# AI Mita Chat Server for Roblox

A Flask-based local AI chat server for the character **Mita**, antagonist from the game **MiSide**.

*Creator:* JustMorDe, Foxan515

---

## 💡 Features

* 💬 **Dynamic Roleplay Personality**: Mita responds with emotional depth and specific behavior based on your prompt.
* 🧠 **Short-Term Memory**: Chat history can be passed from Roblox and reused to simulate memory.
* 🌐 **Model Choice**: Support **Mistral** backend.
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
  "model": "mistral"
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

## ❗ Notes

* The AI will **not** respond if no `prompt` is provided.
* Personality instructions are loaded from `prompts/{LANG}.txt`.

---

## 🧠 Roadmap

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
