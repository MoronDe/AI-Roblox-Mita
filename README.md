# AI Mita — Roblox Server

[![Built with Pollinations](https://img.shields.io/badge/Built%20with-Pollinations-00C7B7)](https://pollinations.ai/)

Flask-based AI server for **Mita**, the antagonist from the game *MiSide*, integrated with Roblox.

**Creator:** JustMorDe, Foxan515  
**Roblox Game:** [The Mita](https://www.roblox.com/games/98105867888961/The-Mita)

---

## 💡 Features

- 💬 **Dynamic Roleplay Personality** — Mita responds with emotional depth and specific behavior based on player input.
- 🧠 **Conversation Memory** — Chat history is passed from Roblox and reused to simulate short-term memory.
- 🤖 **Pollinations AI Integration** — Uses Pollinations AI endpoint for text generation.
- 🎭 **Structured JSON Output** — Responses include character actions, facial expressions, and navigation commands (`goto`).
- 🎮 **Roblox Integration** — The server receives player speech via HTTP and returns actions that the Roblox game uses to animate Mita (hugging, following, teleporting, knife animations, etc.).
- 🛡️ **Spam Protection** — Enforces cooldowns per IP to prevent spam.
- 🗂️ **Request Logging** — Console logs with basic request and response info.

---


## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/MoronDe/AI-Roblox-Mita
cd AI-Roblox-Mita
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


Field	Type	Required	Description
prompt	string	✅ Yes	User's spoken message
lang	string	❌ No	Language: RU or EN (default: RU)
history	array	❌ No	Previous conversation messages


* `prompt` – user message (required)
* `lang` – language code (`RU`/`EN`, default: `RU`)
* `model` – backend to use (`mistral`)
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
* The server is designed to run locally and be called by the Roblox game via HTTP.

---

## 🧠 Roadmap

* [ ] Admin panel for chat history and user stats
* [ ] WebSocket support
* [ ] Fine-tuned emotion/behavior response tuning
* [ ] Bad word filter and request limiter

---

## ⚙️ Dependencies

* `Flask`
* `python-dotenv`
* `requests` - (for Pollinations AI endpoint)

---

## 📄 License

MIT License. Attribution for the character "Mita" belongs to creators of *MiSide*.

## 🔗 Links
* Roblox Game: https://www.roblox.com/games/98105867888961/The-Mita
* GitHub Repository: https://github.com/MoronDe/AI-Roblox-Mita
