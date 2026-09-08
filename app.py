from flask import Flask, render_template, request, jsonify
import ollama
import json
import os
from datetime import datetime

app = Flask(__name__)

MODEL_NAME = "qwen2.5:3b"
KNOWLEDGE_FILE = "knowledge.json"
MEMORY_FILE = "memory.json"


# ============================================================
# JSON FILE FUNCTIONS
# ============================================================

def load_json(filename, default):
    try:
        if not os.path.exists(filename):
            return default

        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as error:
        print(f"Error loading {filename}:", error)
        return default


def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    except Exception as error:
        print(f"Error saving {filename}:", error)


knowledge = load_json(KNOWLEDGE_FILE, {})
memory = load_json(MEMORY_FILE, [])


# ============================================================
# DATE AND TIME
# ============================================================

def get_current_datetime():
    now = datetime.now()

    return {
        "date": now.strftime("%A, %d %B %Y"),
        "time": now.strftime("%I:%M:%S %p")
    }


# ============================================================
# KNOWLEDGE
# ============================================================

def format_knowledge():
    if not knowledge:
        return "No additional knowledge available."

    try:
        return json.dumps(
            knowledge,
            indent=2,
            ensure_ascii=False
        )

    except Exception:
        return str(knowledge)


# ============================================================
# MEMORY
# ============================================================

def get_recent_memory(limit=3):

    if not memory:
        return "No previous conversation."

    recent = memory[-limit:]

    lines = []

    for item in recent:

        if not isinstance(item, dict):
            continue

        user_text = item.get("user", "")
        assistant_text = item.get("assistant", "")

        if user_text:
            lines.append(f"User: {user_text}")

        if assistant_text:
            lines.append(f"Assistant: {assistant_text}")

    if not lines:
        return "No previous conversation."

    return "\n".join(lines)


def add_memory(user_message, assistant_message):

    global memory

    memory.append({
        "user": user_message,
        "assistant": assistant_message,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only the latest 20 conversations
    if len(memory) > 20:
        memory = memory[-20:]

    try:
        save_json(MEMORY_FILE, memory)

    except Exception as error:
        print("Memory save error:", error)


def clear_memory():

    global memory

    memory = []

    try:
        save_json(MEMORY_FILE, memory)

    except Exception as error:
        print("Memory clear error:", error)


# ============================================================
# FAST RESPONSES
# ============================================================

def simple_response(message):

    text = message.lower().strip()

    greetings = {
        "hi": "Hello! How can I help you?",
        "hello": "Hello! How can I help you?",
        "hey": "Hey! How can I help you?",
        "good morning": "Good morning! How can I help you?",
        "good afternoon": "Good afternoon! How can I help you?",
        "good evening": "Good evening! How can I help you?"
    }

    if text in greetings:
        return greetings[text]

    # Date questions
    date_keywords = [
        "what is today's date",
        "what is the date today",
        "today's date",
        "current date",
        "what date is it"
    ]

    if text in date_keywords:

        current = get_current_datetime()

        return f"Today's date is {current['date']}."

    # Time questions
    time_keywords = [
        "what time is it",
        "current time",
        "what is the current time",
        "tell me the time",
        "time now"
    ]

    if text in time_keywords:

        current = get_current_datetime()

        return f"The current time is {current['time']}."

    return None


# ============================================================
# FAST AI PROMPT
# ============================================================

def create_fast_prompt(user_message):

    current = get_current_datetime()

    recent_memory = get_recent_memory(limit=3)

    knowledge_text = format_knowledge()

    prompt = f"""
You are a helpful AI text virtual assistant.

Rules:
- Give clear and direct answers.
- Keep answers reasonably short.
- Be friendly and helpful.
- Use recent conversation when relevant.
- Use the knowledge provided below when relevant.
- Use the current date and time when relevant.
- Do not invent information.
- If the knowledge does not contain the answer, answer normally using your general knowledge.

Current date:
{current["date"]}

Current time:
{current["time"]}

Knowledge:
{knowledge_text}

Recent conversation:
{recent_memory}

User message:
{user_message}
"""

    return prompt


# ============================================================
# OLLAMA
# ============================================================

def ask_ollama(user_message):

    prompt = create_fast_prompt(user_message)

    try:

        print("\nUser:", user_message)
        print("Sending request to Ollama...")

        response = ollama.chat(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],

            options={
                "temperature": 0.2,
                "num_predict": 128
            }
        )

        answer = response["message"]["content"].strip()

        print("Assistant:", answer)

        return answer

    except Exception as error:

        print("Ollama error:", error)

        return (
            "Sorry, I couldn't generate a response right now. "
            "Please make sure Ollama is running and try again."
        )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# CHAT
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "response": "No data received."
            }), 400

        user_message = data.get("message", "").strip()

        if not user_message:

            return jsonify({
                "success": False,
                "response": "Please enter a message."
            }), 400

        # Limit message size
        if len(user_message) > 500:

            return jsonify({
                "success": False,
                "response": "Your message is too long. Please keep it under 500 characters."
            }), 400

        # Try fast response first
        quick_answer = simple_response(user_message)

        if quick_answer:

            try:
                add_memory(
                    user_message,
                    quick_answer
                )

            except Exception as error:
                print("Memory error:", error)

            return jsonify({
                "success": True,
                "response": quick_answer
            })

        # Otherwise use Ollama
        answer = ask_ollama(user_message)

        try:

            add_memory(
                user_message,
                answer
            )

        except Exception as error:

            print("Memory error:", error)

        return jsonify({
            "success": True,
            "response": answer
        })

    except Exception as error:

        print("Chat route error:", error)

        return jsonify({
            "success": False,
            "response": "Something went wrong while processing your message."
        }), 500


# ============================================================
# CLEAR MEMORY
# ============================================================

@app.route("/clear-memory", methods=["POST"])
def clear_memory_route():

    try:

        clear_memory()

        return jsonify({
            "success": True,
            "message": "Memory cleared successfully."
        })

    except Exception as error:

        print("Clear memory error:", error)

        return jsonify({
            "success": False,
            "message": "Could not clear memory."
        }), 500


# ============================================================
# DATE/TIME API
# ============================================================

@app.route("/datetime")
def datetime_route():

    current = get_current_datetime()

    return jsonify({
        "success": True,
        "date": current["date"],
        "time": current["time"]
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "model": MODEL_NAME
    })


# ============================================================
# TEST OLLAMA
# ============================================================

@app.route("/test-ollama")
def test_ollama():

    try:

        start_time = datetime.now()

        response = ollama.chat(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": "Hello"
                }
            ],

            options={
                "temperature": 0.2,
                "num_predict": 50
            }
        )

        elapsed = (
            datetime.now() - start_time
        ).total_seconds()

        return jsonify({

            "success": True,

            "response": response["message"]["content"],

            "time_seconds": round(
                elapsed,
                2
            )

        })

    except Exception as error:

        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# ============================================================
# START FLASK SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI TEXT VIRTUAL ASSISTANT")
    print("=" * 60)

    print(f"Model: {MODEL_NAME}")

    print("Server: http://127.0.0.1:5000")

    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )