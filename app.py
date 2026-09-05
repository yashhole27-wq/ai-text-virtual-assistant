from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import re
import ast
import operator
import json
import os
import math

app = Flask(__name__)

# =========================================================
# APPLICATION SETTINGS
# =========================================================

MAX_MESSAGE_LENGTH = 500

MEMORY_FILE = "memory.json"
KNOWLEDGE_FILE = "knowledge.json"


# =========================================================
# PERSISTENT MEMORY
# =========================================================

def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return {
            "name": None,
            "last_topic": None
        }

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        print("Warning: Could not load memory.json")

    return {
        "name": None,
        "last_topic": None
    }


def save_memory():

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4
            )

    except OSError as error:

        print(
            "Memory save error:",
            error
        )


memory = load_memory()

if "name" not in memory:
    memory["name"] = None

if "last_topic" not in memory:
    memory["last_topic"] = None


# =========================================================
# LOCAL KNOWLEDGE BASE
# =========================================================

def load_knowledge():

    if not os.path.exists(KNOWLEDGE_FILE):
        return {}

    try:

        with open(
            KNOWLEDGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        print(
            "Warning: Could not load knowledge.json"
        )

    return {}


knowledge_base = load_knowledge()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def set_topic(topic):

    memory["last_topic"] = topic

    save_memory()


def get_name():

    return memory.get("name")


# =========================================================
# SAFE CALCULATOR
# =========================================================

OPERATORS = {

    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos

}


def safe_calculate(expression):

    try:

        # Prevent excessively large expressions
        if len(expression) > 100:
            return None

        expression = expression.replace(
            "^",
            "**"
        )

        tree = ast.parse(
            expression,
            mode="eval"
        )

        def calculate(node):

            # -------------------------------------------------
            # NUMBER
            # -------------------------------------------------

            if isinstance(
                node,
                ast.Constant
            ):

                if isinstance(
                    node.value,
                    (int, float)
                ):

                    return node.value

                raise ValueError(
                    "Invalid value"
                )

            # -------------------------------------------------
            # BINARY OPERATION
            # -------------------------------------------------

            if isinstance(
                node,
                ast.BinOp
            ):

                left = calculate(
                    node.left
                )

                right = calculate(
                    node.right
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError(
                        "Invalid operator"
                    )

                # Prevent extremely large exponentiation
                if (
                    isinstance(
                        node.op,
                        ast.Pow
                    )
                    and abs(right) > 100
                ):

                    raise ValueError(
                        "Exponent too large"
                    )

                return operation(
                    left,
                    right
                )

            # -------------------------------------------------
            # UNARY OPERATION
            # -------------------------------------------------

            if isinstance(
                node,
                ast.UnaryOp
            ):

                value = calculate(
                    node.operand
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError(
                        "Invalid operator"
                    )

                return operation(
                    value
                )

            raise ValueError(
                "Invalid expression"
            )

        result = calculate(
            tree.body
        )

        # Avoid non-finite values
        if isinstance(
            result,
            float
        ):

            if not math.isfinite(result):
                return None

        return result

    except (
        ValueError,
        SyntaxError,
        ZeroDivisionError,
        OverflowError
    ):

        return None


# =========================================================
# DATE PARSER
# =========================================================

def parse_date_from_text(message):

    # -----------------------------------------------------
    # DD/MM/YYYY
    # DD-MM-YYYY
    # -----------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b",
        message
    )

    if match:

        day = int(
            match.group(1)
        )

        month = int(
            match.group(2)
        )

        year = int(
            match.group(3)
        )

        try:

            return datetime(
                year,
                month,
                day
            )

        except ValueError:

            return None

    # -----------------------------------------------------
    # DD Month YYYY
    # -----------------------------------------------------

    match = re.search(
        r"\b(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\b",
        message
    )

    if match:

        day = int(
            match.group(1)
        )

        month = match.group(2)

        year = int(
            match.group(3)
        )

        for fmt in [
            "%d %B %Y",
            "%d %b %Y"
        ]:

            try:

                return datetime.strptime(
                    f"{day} {month} {year}",
                    fmt
                )

            except ValueError:

                pass

    # -----------------------------------------------------
    # Month DD YYYY
    # -----------------------------------------------------

    match = re.search(
        r"\b([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})\b",
        message
    )

    if match:

        month = match.group(1)

        day = int(
            match.group(2)
        )

        year = int(
            match.group(3)
        )

        for fmt in [
            "%B %d %Y",
            "%b %d %Y"
        ]:

            try:

                return datetime.strptime(
                    f"{month} {day} {year}",
                    fmt
                )

            except ValueError:

                pass

    return None


# =========================================================
# KNOWLEDGE BASE SEARCH
# =========================================================

def search_knowledge(message):

    text = message.lower().strip()

    all_topics = []

    for topic, data in knowledge_base.items():

        keywords = data.get(
            "keywords",
            []
        )

        answer = data.get(
            "answer",
            ""
        )

        for keyword in keywords:

            all_topics.append(
                (
                    str(keyword).lower(),
                    answer
                )
            )

    # Check longer phrases first
    all_topics.sort(
        key=lambda item: len(item[0]),
        reverse=True
    )

    for keyword, answer in all_topics:

        # Use word boundaries for short keywords
        if len(keyword) <= 3:

            if re.search(
                rf"\b{re.escape(keyword)}\b",
                text
            ):

                return answer

        else:

            if keyword in text:

                return answer

    return None


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    # =====================================================
    # VALIDATE JSON
    # =====================================================

    if not request.is_json:

        return jsonify({
            "response":
            "Please send a valid message request."
        }), 400

    try:

        data = request.get_json(
            silent=True
        )

    except Exception:

        return jsonify({
            "response":
            "Invalid request data."
        }), 400

    if not isinstance(
        data,
        dict
    ):

        return jsonify({
            "response":
            "Invalid request format."
        }), 400

    # =====================================================
    # GET MESSAGE
    # =====================================================

    message = data.get(
        "message",
        ""
    )

    if not isinstance(
        message,
        str
    ):

        return jsonify({
            "response":
            "Message must be text."
        }), 400

    message = message.strip()

    # =====================================================
    # EMPTY MESSAGE
    # =====================================================

    if not message:

        return jsonify({
            "response":
            "Please enter a message."
        })

    # =====================================================
    # MESSAGE LENGTH PROTECTION
    # =====================================================

    if len(message) > MAX_MESSAGE_LENGTH:

        return jsonify({
            "response":
            f"Your message is too long. "
            f"Please keep it under "
            f"{MAX_MESSAGE_LENGTH} characters."
        }), 400

    text = message.lower()

    # =====================================================
    # MAIN PROCESSING
    # =====================================================

    try:

        # =================================================
        # REMEMBER NAME
        # =================================================

        name_match = re.search(
            r"^(?:my name is|i am|i'm|call me|remember my name is)\s+([a-zA-Z]+)",
            text
        )

        if name_match:

            name = name_match.group(
                1
            ).capitalize()

            memory["name"] = name

            set_topic(
                "name"
            )

            response = (
                f"Nice to meet you, {name}! 👋 "
                f"I'll remember your name."
            )

        # =================================================
        # ASK NAME
        # =================================================

        elif (

            "what is my name" in text
            or "what's my name" in text
            or "do you know my name" in text
            or "do you remember my name" in text
            or "can you remember my name" in text
            or "who am i" in text

        ):

            if get_name():

                response = (
                    f"Your name is "
                    f"{get_name()}. 😊"
                )

            else:

                response = (
                    "I don't know your name yet. "
                    "Tell me by saying "
                    "'My name is Yash'."
                )

            set_topic(
                "name"
            )

        # =================================================
        # GREETINGS
        # =================================================

        elif any(

            re.search(
                pattern,
                text
            )

            for pattern in [

                r"^hi\b",
                r"^hello\b",
                r"^hey\b",
                r"^hii\b",
                r"^helo\b",
                r"^hi there\b",
                r"^hello there\b",
                r"good morning",
                r"good afternoon",
                r"good evening"

            ]

        ):

            if get_name():

                response = (
                    f"Hello, {get_name()}! 👋 "
                    f"How can I help you today?"
                )

            else:

                response = (
                    "Hello! 👋 "
                    "I'm your AI Text Virtual Assistant. "
                    "How can I help you today?"
                )

            set_topic(
                "greeting"
            )

        # =================================================
        # HOW ARE YOU
        # =================================================

        elif (

            "how are you" in text
            or "how r you" in text
            or "how are u" in text
            or "how are things" in text
            or "how is it going" in text
            or "how's it going" in text

        ):

            if get_name():

                response = (
                    f"I'm doing great, "
                    f"{get_name()}! 😊 "
                    f"Thanks for asking. "
                    f"How can I help you?"
                )

            else:

                response = (
                    "I'm doing great! 😊 "
                    "Thanks for asking. "
                    "How can I help you?"
                )

            set_topic(
                "conversation"
            )

        # =================================================
        # WHO ARE YOU
        # =================================================

        elif (

            "who are you" in text
            or "what are you" in text
            or "tell me about yourself" in text
            or "introduce yourself" in text

        ):

            response = (
                "I'm an AI-Based Text Virtual "
                "Assistant 🤖. I'm built using "
                "Python and Flask and designed "
                "to understand text-based questions "
                "and provide useful responses."
            )

            set_topic(
                "about"
            )

        # =================================================
        # WHAT CAN YOU DO
        # =================================================

        elif (

            "what can you do" in text
            or "your abilities" in text
            or "your features" in text
            or "what are your features" in text
            or "how can you help me" in text
            or "what do you do" in text

        ):

            response = (
                "I can currently help you with:\n"
                "• 👋 Natural conversation\n"
                "• 🧠 Remembering your name\n"
                "• 💾 Persistent memory\n"
                "• 📚 Local knowledge\n"
                "• ⏰ Current time\n"
                "• 📅 Current date and day\n"
                "• 📆 Date calculations\n"
                "• 🧮 Mathematical calculations\n"
                "• 😂 Jokes"
            )

            set_topic(
                "features"
            )

        # =================================================
        # THANK YOU
        # =================================================

        elif (

            text in [
                "thanks",
                "thank you",
                "thankyou",
                "thanks a lot",
                "thank you so much"
            ]

            or "thanks for your help" in text
            or "thank you for your help" in text

        ):

            response = (
                "You're welcome! 😊 "
                "I'm happy to help."
            )

            set_topic(
                "conversation"
            )

        # =================================================
        # GOOD NIGHT
        # =================================================

        elif (

            "good night" in text
            or "goodnight" in text

        ):

            if get_name():

                response = (
                    f"Good night, "
                    f"{get_name()}! 🌙 "
                    f"Have a great rest!"
                )

            else:

                response = (
                    "Good night! 🌙 "
                    "Have a great rest!"
                )

            set_topic(
                "goodbye"
            )

        # =================================================
        # AI / ROBOT
        # =================================================

        elif (

            "are you a robot" in text
            or "are you an ai" in text
            or "are you artificial intelligence" in text
            or "are you real" in text

        ):

            response = (
                "Yes! 🤖 I'm a computer-based "
                "AI text assistant created using "
                "Python and Flask."
            )

            set_topic(
                "about"
            )

        # =================================================
        # WHO CREATED YOU
        # =================================================

        elif (

            "who created you" in text
            or "who made you" in text
            or "who built you" in text
            or "who developed you" in text

        ):

            response = (
                "I was developed as an AI-Based "
                "Text Virtual Assistant project "
                "using Python and Flask. "
                "My developer is the person "
                "currently working with me. 👨‍💻"
            )

            set_topic(
                "about"
            )

        # =================================================
        # JOKE
        # =================================================

        elif (

            "tell me a joke" in text
            or "tell me joke" in text
            or "make me laugh" in text
            or "say something funny" in text

        ):

            response = (
                "Why did the computer go to "
                "the doctor? 🤖😂\n"
                "Because it had a virus!"
            )

            set_topic(
                "joke"
            )

        # =================================================
        # DAYS UNTIL DATE
        # =================================================

        elif (

            "days until" in text
            or "how many days until" in text
            or "days left until" in text
            or "how long until" in text

        ):

            target_date = parse_date_from_text(
                message
            )

            if target_date:

                today = datetime.now().date()

                difference = (
                    target_date.date()
                    - today
                ).days

                if difference > 0:

                    response = (
                        f"There are {difference} "
                        f"days until "
                        f"{target_date.strftime('%d %B %Y')}. 📅"
                    )

                elif difference == 0:

                    response = (
                        "That date is today! 🎉"
                    )

                else:

                    response = (
                        f"{target_date.strftime('%d %B %Y')} "
                        f"has already passed."
                    )

            else:

                response = (
                    "Please provide a date such as "
                    "25 December 2026 or "
                    "25/12/2026."
                )

            set_topic(
                "date"
            )

        # =================================================
        # SPECIFIC DATE → DAY
        # =================================================

        elif (

            (
                "what day" in text
                or "which day" in text
                or "what weekday" in text
                or "which weekday" in text
                or "day of the week" in text
            )

            and parse_date_from_text(
                message
            )

        ):

            date_object = parse_date_from_text(
                message
            )

            response = (
                f"{date_object.strftime('%d %B %Y')} "
                f"was a "
                f"{date_object.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # CURRENT TIME
        # =================================================

        elif (

            (
                re.search(
                    r"\btime\b",
                    text
                )

                and not re.search(
                    r"\btimer\b",
                    text
                )
            )

            or "what time is it" in text
            or "tell me the time" in text
            or "current time" in text
            or "time right now" in text
            or "do you know the time" in text
            or "can you tell me the time" in text

        ):

            current_time = datetime.now().strftime(
                "%I:%M %p"
            )

            response = (
                f"The current time is "
                f"{current_time}. ⏰"
            )

            set_topic(
                "time"
            )

        # =================================================
        # TOMORROW
        # =================================================

        elif (

            "tomorrow" in text
            or "next day" in text

        ):

            tomorrow = (
                datetime.now()
                + timedelta(days=1)
            )

            response = (
                f"Tomorrow will be "
                f"{tomorrow.strftime('%d %B %Y')}, "
                f"which is a "
                f"{tomorrow.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # YESTERDAY
        # =================================================

        elif (

            "yesterday" in text
            or "previous day" in text

        ):

            yesterday = (
                datetime.now()
                - timedelta(days=1)
            )

            response = (
                f"Yesterday was "
                f"{yesterday.strftime('%d %B %Y')}, "
                f"which was a "
                f"{yesterday.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # NEXT WEEK
        # =================================================

        elif (

            "next week" in text
            or "one week from now" in text

        ):

            next_week = (
                datetime.now()
                + timedelta(days=7)
            )

            response = (
                f"One week from today will be "
                f"{next_week.strftime('%d %B %Y')}, "
                f"which is a "
                f"{next_week.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # LAST WEEK
        # =================================================

        elif (

            "last week" in text
            or "one week ago" in text

        ):

            last_week = (
                datetime.now()
                - timedelta(days=7)
            )

            response = (
                f"One week ago was "
                f"{last_week.strftime('%d %B %Y')}, "
                f"which was a "
                f"{last_week.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # CURRENT DATE
        # =================================================

        elif (

            (
                re.search(
                    r"\bdate\b",
                    text
                )

                or "today's date" in text
                or "todays date" in text
            )

            and (
                "today" in text
                or "current" in text
                or "now" in text
            )

        ):

            current_date = datetime.now().strftime(
                "%d %B %Y"
            )

            response = (
                f"Today's date is "
                f"{current_date}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # FUTURE DATE
        # =================================================

        elif (

            "after" in text
            and re.search(
                r"\bday",
                text
            )

        ):

            match = re.search(
                r"(\d+)\s*days?",
                text
            )

            if match:

                days = int(
                    match.group(1)
                )

                future_date = (
                    datetime.now()
                    + timedelta(days=days)
                )

                response = (
                    f"After {days} days, "
                    f"the date will be "
                    f"{future_date.strftime('%d %B %Y')}, "
                    f"which is a "
                    f"{future_date.strftime('%A')}. 📅"
                )

            else:

                response = (
                    "Please tell me how many days "
                    "you want to calculate."
                )

            set_topic(
                "date"
            )

        # =================================================
        # PAST DATE
        # =================================================

        elif (

            "ago" in text
            and re.search(
                r"\bday",
                text
            )

        ):

            match = re.search(
                r"(\d+)\s*days?",
                text
            )

            if match:

                days = int(
                    match.group(1)
                )

                past_date = (
                    datetime.now()
                    - timedelta(days=days)
                )

                response = (
                    f"{days} days ago was "
                    f"{past_date.strftime('%d %B %Y')}, "
                    f"which was a "
                    f"{past_date.strftime('%A')}. 📅"
                )

            else:

                response = (
                    "Please tell me how many days "
                    "you want to calculate."
                )

            set_topic(
                "date"
            )

        # =================================================
        # CURRENT DAY
        # =================================================

        elif (

            (
                "what day" in text
                or "which day" in text
            )

            and "today" in text

        ):

            current_day = datetime.now().strftime(
                "%A"
            )

            response = (
                f"Today is "
                f"{current_day}. 😊"
            )

            set_topic(
                "date"
            )

        # =================================================
        # NATURAL LANGUAGE CALCULATOR
        # =================================================

        elif (

            "calculate" in text
            or "solve" in text
            or "plus" in text
            or "minus" in text
            or "multiplied by" in text
            or "multiply" in text
            or "divided by" in text
            or "divide" in text
            or "times" in text
            or "mod" in text

            or re.search(
                r"\d+\s*[\+\-\*\/\%\^]\s*\d+",
                text
            )

        ):

            expression = text

            expression = re.sub(
                r"\b(calculate|solve|what is|what's|can you calculate)\b",
                "",
                expression
            )

            expression = re.sub(
                r"\bmultiplied by\b",
                "*",
                expression
            )

            expression = re.sub(
                r"\bmultiply(?: by)?\b",
                "*",
                expression
            )

            expression = re.sub(
                r"\bdivided by\b",
                "/",
                expression
            )

            expression = re.sub(
                r"\bdivide(?: by)?\b",
                "/",
                expression
            )

            expression = re.sub(
                r"\bplus\b",
                "+",
                expression
            )

            expression = re.sub(
                r"\bminus\b",
                "-",
                expression
            )

            expression = re.sub(
                r"\btimes\b",
                "*",
                expression
            )

            expression = re.sub(
                r"\bmod\b",
                "%",
                expression
            )

            expression = expression.replace(
                "×",
                "*"
            )

            expression = expression.replace(
                "÷",
                "/"
            )

            expression = expression.replace(
                "?",
                ""
            )

            expression = expression.strip()

            if re.fullmatch(
                r"[0-9+\-*/().%\s^]+",
                expression
            ):

                result = safe_calculate(
                    expression
                )

                if result is not None:

                    if (
                        isinstance(
                            result,
                            float
                        )
                        and result.is_integer()
                    ):

                        result = int(
                            result
                        )

                    response = (
                        f"{expression} = "
                        f"{result} 🧮"
                    )

                else:

                    response = (
                        "I couldn't calculate that. "
                        "Please check the expression."
                    )

            else:

                response = (
                    "I can calculate expressions such as "
                    "25 plus 8, 50 divided by 5, "
                    "or 12 multiplied by 6."
                )

            set_topic(
                "calculator"
            )

        # =================================================
        # HELP
        # =================================================

        elif (

            text == "help"
            or "i need help" in text
            or "can you help me" in text
            or "show help" in text

        ):

            response = (
                "Sure! 😊 I can help you with:\n"
                "• 👋 Conversation\n"
                "• 🧠 Name memory\n"
                "• 💾 Persistent memory\n"
                "• 📚 Local knowledge\n"
                "• ⏰ Time\n"
                "• 📅 Dates and days\n"
                "• 🗓️ Date calculations\n"
                "• 🧮 Mathematical calculations\n"
                "• 😂 Jokes"
            )

            set_topic(
                "help"
            )

        # =================================================
        # GOODBYE
        # =================================================

        elif text in [

            "bye",
            "goodbye",
            "see you",
            "see you later",
            "talk to you later"

        ]:

            if get_name():

                response = (
                    f"Goodbye, {get_name()}! 👋 "
                    f"Have a great day!"
                )

            else:

                response = (
                    "Goodbye! 👋 "
                    "Have a great day!"
                )

            set_topic(
                "goodbye"
            )

        # =================================================
        # BASIC FOLLOW-UP
        # =================================================

        elif (

            text in [
                "and tomorrow",
                "what about tomorrow",
                "what about the next day"
            ]

            and memory.get(
                "last_topic"
            ) == "date"

        ):

            tomorrow = (
                datetime.now()
                + timedelta(days=1)
            )

            response = (
                f"Tomorrow will be "
                f"{tomorrow.strftime('%d %B %Y')}, "
                f"which is a "
                f"{tomorrow.strftime('%A')}. 📅"
            )

            set_topic(
                "date"
            )

        # =================================================
        # LOCAL KNOWLEDGE BASE
        # =================================================

        else:

            knowledge_response = search_knowledge(
                message
            )

            if knowledge_response:

                response = knowledge_response

                set_topic(
                    "knowledge"
                )

            else:

                response = (
                    "I'm still learning. 🤖 "
                    "You can ask me about the time, "
                    "date, calculations, your name, "
                    "or general topics such as "
                    "Python, SQL, HTML, CSS, AI, "
                    "Machine Learning, DBMS, Flask, "
                    "Data Analysis, and Blockchain."
                )

        # =================================================
        # RETURN RESPONSE
        # =================================================

        return jsonify({
            "response": response
        })

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    except Exception as error:

        print(
            "Chat processing error:",
            error
        )

        return jsonify({
            "response":
            "Sorry, something went wrong while "
            "processing your request. Please try again."
        }), 500


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )