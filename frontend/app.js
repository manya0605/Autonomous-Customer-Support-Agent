const API_BASE_URL = "http://127.0.0.1:8000";


// ==================================================
// AUTH ELEMENTS
// ==================================================

const authContainer = document.getElementById("authContainer");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const loginEmail = document.getElementById("loginEmail");
const loginPassword = document.getElementById("loginPassword");

const registerName = document.getElementById("registerName");
const registerEmail = document.getElementById("registerEmail");
const registerPassword = document.getElementById("registerPassword");
const registerPhone = document.getElementById("registerPhone");

const loginButton = document.getElementById("loginButton");
const registerButton = document.getElementById("registerButton");

const showRegisterButton = document.getElementById("showRegisterButton");
const showLoginButton = document.getElementById("showLoginButton");

const loginMessage = document.getElementById("loginMessage");
const registerMessage = document.getElementById("registerMessage");


// ==================================================
// DASHBOARD ELEMENTS
// ==================================================

const dashboard = document.getElementById("dashboard");

const userAvatar = document.getElementById("userAvatar");
const userName = document.getElementById("userName");

const logoutButton = document.getElementById("logoutButton");

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const messagesContainer = document.getElementById("messages");

let conversationId = "frontend-chat-" + Date.now();


// ==================================================
// SHOW LOGIN
// ==================================================

function showLogin() {

    loginForm.style.display = "block";
    registerForm.style.display = "none";

    loginMessage.textContent = "";
    registerMessage.textContent = "";
}


// ==================================================
// SHOW REGISTER
// ==================================================

function showRegister() {

    loginForm.style.display = "none";
    registerForm.style.display = "block";

    loginMessage.textContent = "";
    registerMessage.textContent = "";
}


// ==================================================
// LOGIN
// ==================================================

async function login() {

    const email = loginEmail.value.trim();
    const password = loginPassword.value;

    if (!email || !password) {

        loginMessage.textContent =
            "Please enter your email and password.";

        return;
    }

    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";
    loginMessage.textContent = "";

    try {

        const response = await fetch(
            `${API_BASE_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {

            loginMessage.textContent =
                data.detail ||
                "Login failed.";

            return;
        }


        // ------------------------------------------
        // SAVE JWT TOKEN
        // ------------------------------------------

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        localStorage.setItem(
            "customer_id",
            data.customer_id
        );


        // ------------------------------------------
        // LOAD CUSTOMER DASHBOARD
        // ------------------------------------------

        await loadCustomerProfile();

        showDashboard();

    } catch (error) {

        console.error(error);

        loginMessage.textContent =
            "Unable to connect to the support server.";

    } finally {

        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
}


// ==================================================
// REGISTER
// ==================================================

async function register() {

    const name = registerName.value.trim();
    const email = registerEmail.value.trim();
    const password = registerPassword.value;
    const phone = registerPhone.value.trim();


    if (!name || !email || !password) {

        registerMessage.textContent =
            "Name, email and password are required.";

        return;
    }


    registerButton.disabled = true;
    registerButton.textContent = "Creating account...";
    registerMessage.textContent = "";


    try {

        const response = await fetch(
            `${API_BASE_URL}/auth/register`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    name: name,
                    email: email,
                    password: password,
                    phone: phone || null

                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            registerMessage.textContent =
                data.detail ||
                "Registration failed.";

            return;
        }


        // ------------------------------------------
        // REGISTRATION SUCCESS
        // ------------------------------------------

        registerMessage.textContent =
            "Account created successfully. Please log in.";


        // Clear registration form

        registerName.value = "";
        registerEmail.value = "";
        registerPassword.value = "";
        registerPhone.value = "";


        // Show login form

        setTimeout(() => {

            showLogin();

            loginEmail.value = email;

        }, 1000);


    } catch (error) {

        console.error(error);

        registerMessage.textContent =
            "Unable to connect to the support server.";

    } finally {

        registerButton.disabled = false;
        registerButton.textContent = "Create Account";
    }
}


// ==================================================
// LOAD CUSTOMER PROFILE
// ==================================================

async function loadCustomerProfile() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/customers/me`,
            {
                method: "GET",

                headers: {
                    "Authorization":
                        `Bearer ${token}`
                }
            }
        );


        if (!response.ok) {

            console.log(
                "Could not load customer profile."
            );

            return;
        }


        const customer = await response.json();


        if (customer.name) {

            userName.textContent =
                customer.name;

            userAvatar.textContent =
                customer.name
                    .charAt(0)
                    .toUpperCase();
        }

    } catch (error) {

        console.error(
            "Profile loading error:",
            error
        );
    }
}


// ==================================================
// SHOW DASHBOARD
// ==================================================

function showDashboard() {

    authContainer.style.display = "none";
    dashboard.style.display = "flex";

    messageInput.focus();
}


// ==================================================
// SHOW AUTH SCREEN
// ==================================================

function showAuth() {

    dashboard.style.display = "none";
    authContainer.style.display = "flex";

    showLogin();
}


// ==================================================
// LOGOUT
// ==================================================

function logout() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("customer_id");

    conversationId =
        "frontend-chat-" + Date.now();

    messagesContainer.innerHTML = "";

    showAuth();
}


// ==================================================
// ADD MESSAGE
// ==================================================

function addMessage(message, sender) {

    const messageElement =
        document.createElement("div");


    if (sender === "assistant") {

        messageElement.className =
            "message assistant-message";

        messageElement.innerHTML = `

            <div class="message-avatar">
                AI
            </div>

            <div class="message-content">

                <div class="message-name">
                    Support AI
                </div>

                <div class="message-bubble">
                    ${message}
                </div>

            </div>
        `;

    } else {

        messageElement.className =
            "message user-message";

        messageElement.innerHTML = `

            <div class="message-content">

                <div class="message-name">
                    You
                </div>

                <div class="message-bubble">
                    ${message}
                </div>

            </div>
        `;
    }


    messagesContainer.appendChild(
        messageElement
    );

    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;
}


// ==================================================
// SEND CHAT MESSAGE
// ==================================================

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {
        return;
    }


    const token =
        localStorage.getItem("access_token");


    if (!token) {

        addMessage(
            "Please log in before using the support assistant.",
            "assistant"
        );

        return;
    }


    // --------------------------------------------------
    // Extract order ID from the user's message
    // Example:
    // "What is the status of order 2?"
    // becomes order_id = 2
    // --------------------------------------------------

    let orderId = null;

    const orderMatch = message.match(
        /\border\s*#?\s*(\d+)\b/i
    );

    if (orderMatch) {
        orderId = Number(orderMatch[1]);
    }


    addMessage(
        message,
        "user"
    );


    messageInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Sending...";


    try {

        const requestBody = {

            message: message,

            conversation_id:
                conversationId
        };


        // Only send order_id when an order number
        // was actually found in the user's message.
        if (orderId !== null) {

            requestBody.order_id =
                orderId;
        }


        const response = await fetch(
            `${API_BASE_URL}/agent/chat`,
            {
                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json",

                    "Authorization":
                        `Bearer ${token}`
                },

                body: JSON.stringify(
                    requestBody
                )
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            addMessage(

                data.detail ||
                "Something went wrong while contacting the support agent.",

                "assistant"

            );

            return;
        }


        addMessage(

            data.response ||
            "I was unable to process your request.",

            "assistant"

        );


        if (data.conversation_id) {

            conversationId =
                data.conversation_id;
        }


    } catch (error) {

        console.error(error);

        addMessage(

            "Unable to connect to the support server. Please make sure the FastAPI backend is running.",

            "assistant"

        );

    } finally {

        sendButton.disabled = false;
        sendButton.textContent = "Send";

        messageInput.focus();
    }
}


// ==================================================
// EVENT LISTENERS
// ==================================================

showRegisterButton.addEventListener(
    "click",
    showRegister
);

showLoginButton.addEventListener(
    "click",
    showLogin
);

loginButton.addEventListener(
    "click",
    login
);

registerButton.addEventListener(
    "click",
    register
);

logoutButton.addEventListener(
    "click",
    logout
);

sendButton.addEventListener(
    "click",
    sendMessage
);


messageInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();
        }
    }
);


// ==================================================
// AUTO LOGIN IF TOKEN EXISTS
// ==================================================

async function initializeApp() {

    const token =
        localStorage.getItem("access_token");


    if (!token) {

        showAuth();

        return;
    }


    await loadCustomerProfile();

    showDashboard();
}


initializeApp();