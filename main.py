from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os, json, re, logging, warnings, signal
import emoji

load_dotenv()
warnings.filterwarnings("ignore", category=UserWarning) # Sybau plzz

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

def extract_action_from_output(text):
    action = face = player_face = goto = None
    json_matches = re.findall(r'\{.*?\}', text, flags=re.DOTALL)
    for json_str in json_matches:
        try:
            data = json.loads(json_str)
            raw_action = data.get("action", action)
            if isinstance(raw_action, str) and ',' in raw_action:
                action = [a.strip() for a in raw_action.split(',')]
            else:
                action = raw_action
            face = data.get("face") or data.get("facial expression", face)
            player_face = data.get("player_face", player_face)
            goto = data.get("goto", goto)
            text = text.replace(json_str, '')
        except json.JSONDecodeError:
            continue
    return action, face, player_face, goto, text.strip() or "..."

def load_prompt(character="Crazy Mita", language="EN"):
    path = os.path.join("prompts", character, f"{language}.txt")
    if not os.path.exists(path):
        fallback = os.path.join("prompts", character, "EN.txt")
        if os.path.exists(fallback):
            path = fallback
        else:
            raise FileNotFoundError(f"Prompt not found for {character} in {language}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({'error': 'No prompt provided'}), 400

    user_prompt = data['prompt'].strip()
    history = data.get('history', [])
    lang = data.get('lang', 'RU').upper()
    model_choice = data.get('model', 'gemini')
    character = data.get('character', 'Crazy Mita')
    character_instructions = load_prompt(character, lang)

    try:
        if model_choice == 'gemini':
            gemini_model = genai.GenerativeModel("gemini-2.0-flash")
            messages = [{"role": "model", "parts": [{"text": character_instructions}]}]

            for msg in history:
                messages.append({"role": "user", "parts": [{"text": msg["user"]}]})
                messages.append({"role": "assistant", "parts": [{"text": msg["assistant"]["content"]}]})

            messages.append({"role": "user", "parts": [{"text": user_prompt}]})

            completion = gemini_model.generate_content(
                messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.65,
                    top_p=0.9,
                    max_output_tokens=500
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
            f"Prompt: {user_prompt} | Model: {model_choice} | "
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