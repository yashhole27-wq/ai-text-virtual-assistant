# 🤖 AI-Based Text Virtual Assistant

A lightweight, text-based virtual assistant built with **Python and Flask**. The assistant can understand natural-language queries, perform calculations, provide date and time information, remember the user's name, and answer technical questions using a local knowledge base.

## 📌 Project Overview

The AI-Based Text Virtual Assistant is a web-based assistant designed to provide useful responses through a simple and professional chat interface.

Unlike voice assistants, this project focuses entirely on **text-based interaction** and runs locally without requiring paid AI APIs.

The project demonstrates practical implementation of:

* Python programming
* Flask web development
* Natural-language pattern matching
* Persistent conversation memory
* Date and time processing
* Safe mathematical calculations
* JSON-based knowledge management
* HTML, CSS, and JavaScript frontend development
* Input validation and error handling

## ✨ Features

### 💬 General Conversation

* Greetings
* Thank-you responses
* Good-night responses
* "How are you?"
* "Who are you?"
* "What can you do?"
* AI/robot-related questions
* Creator-related questions
* Simple jokes

### 🕐 Date & Time

The assistant can provide:

* Current time
* Current date
* Current day
* Tomorrow's date
* Yesterday's date
* Next week's date
* Previous week's date
* Date after a specified number of days
* Date a specified number of days ago
* Weekday for a specific date
* Number of days until a specified date

### 🧮 Calculator

Supports natural-language calculations such as:

* `25 plus 8`
* `100 minus 37`
* `12 multiplied by 6`
* `50 divided by 5`
* `10 times 5`
* Basic arithmetic expressions

The calculator uses a safe expression parser rather than Python's `eval()` function.

### 🧠 Conversation Memory

The assistant can remember the user's name during conversations.

Examples:

* `My name is Yash`
* `I am Yash`
* `Call me Yash`
* `Remember my name is Yash`

The memory is stored locally in `memory.json`.

> `memory.json` is excluded from GitHub using `.gitignore` because it may contain personal information.

### 📚 Knowledge Base

The assistant includes a local knowledge base covering technical topics such as:

* Python
* SQL
* HTML
* CSS
* Flask
* Artificial Intelligence
* Machine Learning
* DBMS
* Blockchain
* Data Analysis
* Computer Engineering

The knowledge base can be expanded by adding new topics to `knowledge.json`.

### 🔐 Security & Error Handling

The application includes:

* JSON request validation
* Message type validation
* Maximum message length validation
* Safe mathematical expression evaluation
* Division-by-zero handling
* Exponentiation protection
* File loading error handling
* Friendly error responses

## 🛠️ Technologies Used

| Technology | Purpose                         |
| ---------- | ------------------------------- |
| Python     | Backend logic                   |
| Flask      | Web framework                   |
| HTML       | Web page structure              |
| CSS        | User interface styling          |
| JavaScript | Chat interaction                |
| JSON       | Knowledge base and local memory |
| Git        | Version control                 |

## 📂 Project Structure

```text
ai-text-virtual-assistant/
│
├── app.py
├── knowledge.json
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── script.js
│
├── templates/
│   └── index.html
│
└── memory.json
```

> `memory.json` is created/used locally and is intentionally excluded from GitHub.

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd ai-text-virtual-assistant
```

### 3. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.venv\Scripts\activate
```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

### 6. Run the application

```powershell
python app.py
```

### 7. Open the application

Open the local Flask address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## 💡 Example Queries

Try asking:

```text
Hello
What time is it?
What is today's date?
What day is tomorrow?
What is 25 plus 8?
What is 100 divided by 5?
My name is Yash
What is my name?
What is Python?
What is SQL?
What is Machine Learning?
How many days until 25/12/2026?
```

## 🎯 Learning Outcomes

Through this project, I gained practical experience in:

* Developing a Flask-based web application
* Connecting frontend and backend components
* Handling HTTP requests and JSON data
* Implementing natural-language pattern matching
* Working with regular expressions
* Managing persistent local data
* Building a safe calculator
* Designing a responsive web interface
* Implementing input validation
* Using Git and GitHub for project management

## 🔮 Future Enhancements

Possible future improvements include:

* Integration with a free/low-cost AI API
* More advanced natural-language understanding
* Larger knowledge base
* User authentication
* Conversation history
* Database integration
* Voice input and output
* Deployment to a cloud platform
* More intelligent contextual conversations

## 👨‍💻 Author

**Yash Sachin Hole**

B.E. Computer Engineering
Dattakala Group of Institutions Faculty of Engineering
Savitribai Phule Pune University

---

⭐ If you find this project useful, consider giving the repository a star!
