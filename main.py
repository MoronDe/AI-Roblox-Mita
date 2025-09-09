from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os, json, re, logging, warnings, signal
import emoji

load_dotenv()
warnings.filterwarnings("ignore", category=UserWarning) # sybau plz

logger = logging.getLogger("MitaAI")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

port = 25005

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_KEY)

app = Flask(__name__)

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
        cleaned_text = "..."

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
    character_instructions = load_prompt(character, lang)

    try:
        if model_choice == 'gemini':
            gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            messages = [{"role": "model", "parts": [{"text": character_instructions}]}]

            for msg in history:
                user_text = msg.get("user")
                assistant_text = msg.get("assistant", {}).get("content")
                if user_text:
                    messages.append({"role": "user", "parts": [{"text": user_text}]})
                if assistant_text:
                    messages.append({"role": "assistant", "parts": [{"text": assistant_text}]})

            for ev in events:
                messages.append({"role": "user", "parts": [{"text": f"(EVENT) {ev}"}]})

            if not events and user_prompt:
                messages.append({"role": "user", "parts": [{"text": user_prompt}]})

            completion = gemini_model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    max_output_tokens=350,
                )
            )
            if completion.candidates and completion.candidates[0].content.parts:
                answer_generated = completion.candidates[0].content.parts[0].text.strip()
            else:
                answer_generated = "..."
        else:
            return jsonify({'error': 'Invalid model choice'}), 400

        answer_generated = remove_emojis(answer_generated)
        answer_generated = clean_markdown_blocks(answer_generated)
        action, face, player_face, goto, cleaned_response = extract_action_from_output(answer_generated)
        logger.info(
            f"Prompt: {user_prompt} | Events: {events} | Model: {model_choice} | "
            f"Response: {cleaned_response} | Action: {action} | Goto: {goto}"
        )

    except Exception as e:
        logger.exception("Exception during /ask")
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'response': cleaned_response,
        'action': action,
        'face': face,
        'player_face': player_face,
        'goto': goto,
    })

@app.route('/')
def home():
    return "AI Mita is running."

signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)