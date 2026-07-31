import os
from datetime import date, timedelta

from flask import Flask, render_template, request, jsonify

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from database import (
    init_db,
    save_mood,
    get_all_moods,
    get_today_mood,
    get_statistics
)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "mindcare-secret-key"
)


# Inicializo databazen
init_db()


# -----------------------------
# Mood Analysis
# -----------------------------

MOOD_KEYWORDS = {

    "happy": [
        "happy",
        "great",
        "good",
        "awesome",
        "excited",
        "love",
        "fantastic",
        "joy"
    ],

    "sad": [
        "sad",
        "lonely",
        "down",
        "cry",
        "hurt",
        "depressed",
        "bad"
    ],

    "anxious": [
        "anxious",
        "stress",
        "worried",
        "panic",
        "nervous",
        "afraid"
    ],

    "angry": [
        "angry",
        "mad",
        "frustrated",
        "annoyed"
    ],

    "calm": [
        "calm",
        "relaxed",
        "peaceful",
        "fine",
        "okay",
        "better"
    ]

}


CRISIS_WORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "hurt myself",
    "self harm"
]


def analyze_mood(text):

    text = text.lower()

    for word in CRISIS_WORDS:
        if word in text:
            return "crisis"


    scores = {}

    for mood, words in MOOD_KEYWORDS.items():

        scores[mood] = sum(
            1 for w in words if w in text
        )


    result = max(scores, key=scores.get)


    if scores[result] == 0:
        return "neutral"


    return result



# -----------------------------
# Supportive Response
# -----------------------------

def local_response(mood):

    responses = {

        "happy":
        "I'm happy to hear that. Keep enjoying this positive moment.",


        "sad":
        "I'm sorry you are feeling this way. Try taking a small break and talk with someone you trust.",


        "anxious":
        "It sounds stressful. Try slow breathing and focus on things you can control.",


        "angry":
        "It's okay to feel angry. Take a moment before reacting.",


        "calm":
        "That's wonderful. Maintaining calm moments is important.",


        "neutral":
        "Thank you for sharing. I'm here to listen.",


        "crisis":
        "I'm really glad you shared this. If you feel you may hurt yourself, please contact emergency services or someone you trust immediately."

    }


    return responses.get(
        mood,
        responses["neutral"]
    )



# -----------------------------
# OpenAI Assistant
# -----------------------------


def openai_response(message, mood):

    key = os.environ.get(
        "OPENAI_API_KEY"
    )


    if not key or OpenAI is None:
        return None


    try:

        client = OpenAI(
            api_key=key
        )


        result = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[

                {
                    "role": "system",
                    "content":
                    """
                    You are MindCare AI.
                    Give short supportive answers.
                    Do not diagnose.
                    Encourage professional help when needed.
                    """
                },

                {
                    "role": "user",
                    "content":
                    f"""
                    Mood: {mood}
                    Message: {message}
                    """
                }

            ],

            temperature=0.7
        )


        return (
            result
            .choices[0]
            .message
            .content
        )


    except Exception:

        return None



# -----------------------------
# Pages
# -----------------------------


@app.route("/")
def home():

    return render_template(
        "dashboard.html"
    )



# -----------------------------
# Daily Check-in
# -----------------------------


@app.route(
    "/checkin",
    methods=["POST"]
)
def checkin():

    data = request.json

    message = data.get(
        "message",
        ""
    )


    mood = analyze_mood(
        message
    )


    today = date.today().isoformat()


    existing = get_today_mood()


    if not existing:

        save_mood(
            today,
            mood,
            message
        )


    return jsonify({

        "mood": mood,

        "response":
        local_response(mood)

    })



# -----------------------------
# Chat
# -----------------------------


@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.json

    message = data.get(
        "message",
        ""
    )


    mood = analyze_mood(
        message
    )


    if mood == "crisis":

        reply = local_response(
            mood
        )

    else:

        reply = openai_response(
            message,
            mood
        )


        if reply is None:

            reply = local_response(
                mood
            )


    return jsonify({

        "mood": mood,

        "response": reply

    })



# -----------------------------
# Dashboard Data
# -----------------------------


@app.route(
    "/dashboard-data"
)
def dashboard_data():

    stats = get_statistics()

    moods = get_all_moods()


    today = date.today()

    week = []


    for i in range(7):

        d = (
            today -
            timedelta(days=6-i)
        ).isoformat()


        item = next(
            (
                x for x in moods
                if x["date"] == d
            ),
            None
        )


        week.append({

            "date": d,

            "mood":
            item["mood"]
            if item
            else "none"

        })


    return jsonify({

        "statistics": stats,

        "weekly": week

    })



if __name__ == "__main__":

    app.run(
        debug=True
    )