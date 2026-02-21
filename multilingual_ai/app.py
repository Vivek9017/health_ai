from flask import Flask, render_template, request, Response
import json
import ollama
from gtts import gTTS
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Ensure static/tts folder exists
TTS_FOLDER = os.path.join("static", "tts")
os.makedirs(TTS_FOLDER, exist_ok=True)

LANG_MAP = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr"
}

def build_system_prompt(language):
    if language == "Hindi":
        return """
आप एक सहायक मेडिकल असिस्टेंट हैं।
सिर्फ हिंदी में उत्तर दें और केवल देवनागरी लिपि का उपयोग करें।
रोमन हिंदी का उपयोग न करें।
सरल भाषा में बीमारी की जानकारी दें और सलाह दें।
अंत में लिखें:
'यह AI द्वारा जनित सूचना है — कृपया किसी प्रमाणित डॉक्टर से सलाह लें।'
"""
    elif language == "Marathi":
        return """
तुम्ही एक सहाय्यक वैद्यकीय सहाय्यक आहात.
फक्त मराठीमध्ये उत्तर द्या आणि फक्त देवनागरी लिपी वापरा.
रोमन मराठी वापरू नका.
सोप्या भाषेत आजाराबद्दल माहिती द्या आणि सल्ला द्या.
शेवटी लिहा:
'हे AI द्वारे तयार केलेले आहे — कृपया प्रमाणित डॉक्टरांचा सल्ला घ्या.'
"""
    else:
        return """
You are a helpful medical assistant.
Respond only in English.
Explain the condition clearly and give simple advice.
End with:
'This is AI-generated advice. Please consult a certified doctor.'
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.json
        user_message = data.get("message", "")
        language = data.get("language", "English")

        system_prompt = build_system_prompt(language)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = ollama.chat(
            model="llama3",
            messages=messages
        )

        ai_reply = response["message"]["content"]

        # Generate TTS file
        tts_lang = LANG_MAP.get(language, "en")
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(TTS_FOLDER, filename)

        tts = gTTS(text=ai_reply, lang=tts_lang)
        tts.save(file_path)

        tts_url = f"/static/tts/{filename}"

        payload = {
            "reply": ai_reply,
            "tts_url": tts_url
        }

        return Response(
            json.dumps(payload, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

    except Exception as e:
        return Response(
            json.dumps({"reply": f"Error: {str(e)}", "tts_url": None}, ensure_ascii=False),
            content_type="application/json; charset=utf-8"
        )

if __name__ == "__main__":
    app.run(debug=True)