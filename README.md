# 🤖 AI-Based Text Virtual Assistant

A lightweight, web-based **AI Text Virtual Assistant** built using **Python, Flask, Ollama, and Qwen 2.5**. The assistant provides natural-language responses through a clean chat interface and supports conversation memory, knowledge-based responses, and date/time information.

The application runs **locally**, using a locally installed AI model instead of requiring a paid cloud AI API.

---

## 📌 Project Overview

The AI-Based Text Virtual Assistant is a local web application designed to provide helpful responses through a simple and professional chat interface.

The project focuses on **text-based interaction** and demonstrates how a Python backend can be connected with a locally running Large Language Model (LLM).

### The project demonstrates:

* Python programming
* Flask web development
* Local AI/LLM integration
* Ollama model integration
* Natural-language interaction
* Persistent conversation memory
* JSON-based knowledge management
* Date and time processing
* HTML, CSS, and JavaScript frontend development
* Input validation
* Error handling
* Git and GitHub workflow

---

## ✨ Features

### 💬 AI Chat

The assistant can answer general and technical questions using the locally running **Qwen 2.5:3B** model.

Example:

```text
What is Python?
Explain machine learning.
What is SQL?
What is Flask?
```

---

### 🧠 Conversation Memory

The assistant stores recent conversations locally in `memory.json`.

This allows the assistant to use recent conversation context when answering follow-up questions.

Example:

```text
User: My favorite programming language is Python.

User: What is my favorite programming language?

Assistant: Your favorite programming language is Python.
```

The application keeps a limited number of recent conversations to help maintain good response speed.

> `memory.json` is excluded from GitHub using `.gitignore` because it can contain personal conversation data.

---

### 📚 Knowledge Base

The project includes a local knowledge base stored in:

```text
knowledge.json
```

The knowledge base can contain information about topics such as:

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

The knowledge base can be expanded by adding additional information to `knowledge.json`.

---

### 🕐 Date & Time

The assistant can provide current date and time information.

Examples:

```text
What is today's date?

What time is it?

What is the current date?

What is the current time?
```

The application also includes a dedicated date/time endpoint.

---

### ⚡ Fast Local AI Responses

The project is optimized to keep the AI prompt lightweight by using:

* Recent conversation context
* Local knowledge
* A lightweight Qwen model
* Limited response length

This helps maintain fast responses while running the AI locally.

---

### 🛡️ Input Validation & Error Handling

The application includes:

* Empty message validation
* Maximum message length validation
* JSON request validation
* Ollama error handling
* File loading error handling
* Memory save error handling
* Friendly error messages

---

## 🛠️ Technologies Used

| Technology  | Purpose                         |
| ----------- | ------------------------------- |
| Python      | Backend programming             |
| Flask       | Web framework                   |
| Ollama      | Local AI model runtime          |
| Qwen 2.5:3B | Local language model            |
| HTML        | Web page structure              |
| CSS         | User interface styling          |
| JavaScript  | Chat interaction                |
| JSON        | Knowledge base and local memory |
| Git         | Version control                 |
| GitHub      | Project hosting                 |

---

## 📂 Project Structure

```text
ai-text-virtual-assistant/
│
├── app.py
├── knowledge.json
├── memory.json
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
└── templates/
    └── index.html
```

> `memory.json` is used locally and should not be uploaded to GitHub because it may contain personal conversation data.

---

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

### 5. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 6. Install and run Ollama

Install Ollama on your system and make sure the required model is available:

```powershell
ollama pull qwen2.5:3b
```

Check the installed model:

```powershell
ollama list
```

### 7. Run the Flask application

```powershell
python app.py
```

### 8. Open the application

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

---

## 💡 Example Queries

Try asking the assistant:

```text
Hello

What is Python?

Explain machine learning.

What is SQL?

What is Flask?

What is artificial intelligence?

What is my favorite programming language?

What do you know about me?

What is today's date?

What time is it?
```

---

## 🎯 Learning Outcomes

Through this project, I gained practical experience in:

* Developing a Flask-based web application
* Connecting frontend and backend components
* Handling HTTP requests and JSON data
* Integrating a local Large Language Model
* Working with Ollama
* Using persistent local data
* Building a JSON-based knowledge system
* Managing conversation memory
* Designing a responsive web interface
* Implementing input validation
* Handling application errors
* Using Git and GitHub for project management

---

## 🔮 Future Enhancements

Possible future improvements include:

* More advanced contextual conversations
* Larger and more structured knowledge base
* Database integration
* User authentication
* Conversation history management
* Voice input and output
* Cloud deployment
* Improved natural-language understanding
* Additional AI models
* More advanced Retrieval-Augmented Generation (RAG)

---

## 👨‍💻 Author

**Yash Sachin Hole**

B.E. Computer Engineering
Dattakala Group of Institutions Faculty of Engineering
Savitribai Phule Pune University

---

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

```

### After you replace it

Save with **Ctrl + S**.

Then we have only the **final GitHub cleanup** left. We won't make any more unnecessary code changes. 🚀
```
## 📸 Project Screenshots

### Past Date/Time Query

![Past Date/Time Query](screenshots/1.png)

### Current Date/Time Query

![Current Date/Time Query](screenshots/2.png)

### Future Date/Time Query

![Future Date/Time Query](screenshots/3.png)
