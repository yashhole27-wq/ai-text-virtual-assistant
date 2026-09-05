const input = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const clearButton = document.getElementById("clear-button");

const chatContainer = document.querySelector(".chat-container");
const typingIndicator = document.getElementById("typing-indicator");


// =====================================================
// GET CURRENT TIME
// =====================================================

function getCurrentTime() {

    const now = new Date();

    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


// =====================================================
// ADD MESSAGE
// =====================================================

function addMessage(sender, message, className) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", className);

    const isUser = className === "user-message";

    const avatar = isUser ? "👤" : "🤖";

    messageDiv.innerHTML = `
        <div class="avatar ${isUser ? "user-avatar" : "assistant-avatar"}">
            ${avatar}
        </div>

        <div class="message-wrapper">

            <div class="message-label">
                ${sender}
            </div>

            <div class="message-content">
                ${escapeHtml(message).replace(/\n/g, "<br>")}
            </div>

            <div class="message-time">
                ${getCurrentTime()}
            </div>

        </div>
    `;

    chatContainer.appendChild(messageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}


// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// =====================================================
// SHOW TYPING
// =====================================================

function showTyping() {

    typingIndicator.classList.remove("hidden");

    chatContainer.scrollTop = chatContainer.scrollHeight;
}


// =====================================================
// HIDE TYPING
// =====================================================

function hideTyping() {

    typingIndicator.classList.add("hidden");
}


// =====================================================
// SEND MESSAGE
// =====================================================

async function sendMessage() {

    const message = input.value.trim();

    if (message === "") {
        return;
    }

    if (message.length > 500) {

        addMessage(
            "Assistant",
            "Your message is too long. Please keep it under 500 characters.",
            "assistant-message"
        );

        return;
    }


    // Add user's message
    addMessage(
        "You",
        message,
        "user-message"
    );


    // Clear input
    input.value = "";


    // Disable controls
    input.disabled = true;
    sendButton.disabled = true;


    // Show typing animation
    showTyping();


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });


        const data = await response.json();


        // Small delay for natural typing effect
        await new Promise(resolve => setTimeout(resolve, 400));


        hideTyping();


        if (response.ok) {

            addMessage(
                "Assistant",
                data.response,
                "assistant-message"
            );

        } else {

            addMessage(
                "Assistant",
                data.response || "Something went wrong.",
                "assistant-message"
            );
        }


    } catch (error) {

        hideTyping();

        addMessage(
            "Assistant",
            "Sorry, I couldn't connect to the server. ❌",
            "assistant-message"
        );

        console.error(error);

    } finally {

        input.disabled = false;
        sendButton.disabled = false;

        input.focus();
    }
}


// =====================================================
// CLEAR CHAT
// =====================================================

function clearChat() {

    const confirmed = confirm(
        "Are you sure you want to clear the conversation?"
    );

    if (!confirmed) {
        return;
    }


    chatContainer.innerHTML = `

        <div class="message assistant-message">

            <div class="avatar assistant-avatar">
                🤖
            </div>

            <div class="message-wrapper">

                <div class="message-label">
                    Assistant
                </div>

                <div class="message-content">
                    Chat cleared! 👋
                    <br><br>
                    How can I help you?
                </div>

                <div class="message-time">
                    ${getCurrentTime()}
                </div>

            </div>

        </div>
    `;
}


// =====================================================
// SEND BUTTON
// =====================================================

sendButton.addEventListener("click", sendMessage);


// =====================================================
// ENTER KEY
// =====================================================

input.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }

});


// =====================================================
// CLEAR BUTTON
// =====================================================

clearButton.addEventListener("click", clearChat);


// =====================================================
// AUTO FOCUS
// =====================================================

input.focus();