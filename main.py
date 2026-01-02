import os, json, re, logging, warnings, signal, requests, time
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mistralai import Mistral
import emoji

load_dotenv()
warnings.filterwarnings("ignore", category=UserWarning) # sybau plz

logger = logging.getLogger("MitaAI")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

port = 25005
POLLINATIONS_TOKEN = os.getenv("POLLINATIONS_TOKEN")
if not POLLINATIONS_TOKEN:
    raise RuntimeError("POLLINATIONS_TOKEN not set")

app = Flask(__name__)
last_request_time = {}
COOLDOWN = 3

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')

def clean_markdown_blocks(text: str) -> str:
    return re.sub(r"```(?:json|[\w]*)\s*|\s*```", "", text)

def extract_action_from_output(text: str):
    action = None
    face = None
    player_face = None
    goto = None
    def try_parse_json(s):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None
    json_matches = re.findall(r'\{.*?\}', text, flags=re.DOTALL)
    for json_str in json_matches:
        data = try_parse_json(json_str)
        if not data:
            continue
        raw_action = data.get("action")
        if isinstance(raw_action, str):
            if ',' in raw_action:
                action = [a.strip() for a in raw_action.split(',')]
            else:
                action = raw_action.strip()
        elif isinstance(raw_action, list):
            action = raw_action
        face = data.get("face") or face
        player_face = data.get("player_face") or player_face
        goto = data.get("goto") or goto
        text = text.replace(json_str, '')
    cleaned_text = text.strip()
    if not cleaned_text:
        cleaned_text = ""
    return action, face, player_face, goto, cleaned_text

def load_prompt(character="Crazy Mita", language="EN"):
    base_path = os.path.join("prompts", character)
    path = os.path.join(base_path, f"{language}.txt")
    if not os.path.exists(path):
        fallback = os.path.join(base_path, "EN.txt")
        if os.path.exists(fallback):
            path = fallback
        else:
            return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.before_request
def apply_cooldown():
    if request.endpoint == "ask":
        ip = request.remote_addr
        now = time.time()
        last_time = last_request_time.get(ip, 0)
        if now - last_time < COOLDOWN:
            return jsonify({"error": f"Cooldown {COOLDOWN} sec"}), 429
        last_request_time[ip] = now

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user_prompt = data.get('prompt', '').strip()
    history = data.get('history', [])
    events = data.get('events', [])
    lang = data.get('lang', 'RU').upper()
    model_choice = data.get('model', 'gemini')
    character = data.get('character', 'Crazy Mita')
    customAPI = data.get('customAPI', '')

    character_instructions = load_prompt(character, lang)

    try:
        # ===== OpenAI-style messages =====
        messages = [{"role": "system", "content": character_instructions}]

        for msg in history:
            if msg.get("user"):
                messages.append({"role": "user", "content": msg["user"]})
            if msg.get("assistant", {}).get("content"):
                messages.append({"role": "assistant", "content": msg["assistant"]["content"]})

        for ev in events:
            messages.append({"role": "user", "content": f"(EVENT) {ev}"})

        if not events and user_prompt:
            messages.append({"role": "user", "content": user_prompt})

        answer_generated = ""

        # ============================================================
        # ====================== CUSTOM API ==========================
        # ============================================================
        if customAPI:
            if model_choice == "gemini":
                client = genai.Client(api_key=customAPI)

                contents = []
                for m in messages:
                    contents.append(
                        types.Content(
                            role=m["role"],
                            parts=[types.Part(text=m["content"])]
                        )
                    )

                resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        top_p=0.8,
                        max_output_tokens=350,
                    )
                )

                if resp.candidates:
                    parts = resp.candidates[0].content.parts
                    answer_generated = "".join(p.text for p in parts if p.text).strip()

            elif model_choice == "mistral":
                mistral_client = Mistral(api_key=customAPI)
                chat_response = mistral_client.chat.complete(
                    model="mistral-small-latest",
                    messages=messages
                )
                answer_generated = chat_response.choices[0].message.content.strip()

            else:
                return jsonify({'error': 'Invalid model choice'}), 400

        # ============================================================
        # ====================== POLLINATIONS ========================
        # ============================================================
        else:
            url = "https://text.pollinations.ai/openai"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_TOKEN}",
                "Content-Type": "application/json"
            }

            if model_choice == "gemini":
                payload = {
                    "model": "gemini-2.5-flash-lite",
                    "messages": messages,
                    "stream": False
                }
            elif model_choice == "mistral":
                payload = {
                    "model": "mistral-small-3.1-24b-instruct",
                    "messages": messages,
                    "stream": False
                }
            else:
                return jsonify({'error': 'Invalid model choice'}), 400

            r = requests.post(url, headers=headers, json=payload, timeout=20)
            resp_json = r.json()

            if "choices" in resp_json and resp_json["choices"]:
                msg = resp_json["choices"][0].get("message", {})
                content = msg.get("content")

                if isinstance(content, str):
                    answer_generated = content.strip()
                elif isinstance(content, list):
                    answer_generated = "".join(
                        part.get("text", "")
                        for part in content
                        if isinstance(part, dict)
                    ).strip()

        # ===================== POST PROCESS =====================

        answer_generated = remove_emojis(answer_generated)
        answer_generated = clean_markdown_blocks(answer_generated)

        action, face, player_face, goto, cleaned_response = extract_action_from_output(
            answer_generated
        )

        if not cleaned_response:
            cleaned_response = "..."

        logger.info(
            f"Prompt: {user_prompt} | Events: {events} | "
            f"Model: {model_choice} | CustomAPI: {bool(customAPI)} | "
            f"Response: {cleaned_response} | Action: {action} | Goto: {goto}"
        )

    except Exception as e:
        logger.exception("Exception during /ask")
        return jsonify({'error': str(e)}), 500

    return jsonify({
        "response": cleaned_response,
        "action": action,
        "face": face,
        "player_face": player_face,
        "goto": goto,
    })

@app.route('/')
def home():
    return "AI Mita is running."

signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)