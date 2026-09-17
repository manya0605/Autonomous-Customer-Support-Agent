# 🤖 Autonomous Customer Support Agent

An AI-powered customer support system that autonomously understands customer requests, routes them to specialized agents, performs secure business actions, retrieves company knowledge using RAG, and escalates complex issues to human support when required.

## 🚀 Features

- 🔐 JWT-based customer authentication
- 👤 Customer-specific data authorization
- 🤖 Multi-agent support orchestration
- 📦 Order status and tracking
- 💳 Payment information handling
- 🔄 Return request creation and status tracking
- ❌ Order cancellation
- 🎫 Support ticket creation and retrieval
- 📚 RAG-based company knowledge retrieval
- 🧠 Intent detection and sentiment analysis
- 🛠️ Automated troubleshooting
- 👨‍💼 Human escalation for complex issues
- 💬 Conversation history
- 🛡️ Cross-customer data isolation
- 🧪 Automated security tests
- ⚙️ GitHub Actions CI

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │      Customer    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    Web Frontend  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   FastAPI API    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ JWT Authentication│
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Support Orchestrator     │
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
       ┌──────────┐        ┌──────────┐       ┌──────────┐
       │  Order   │        │ Payment  │       │  Return  │
       │  Agent   │        │  Agent   │       │  Flow    │
       └──────────┘        └──────────┘       └──────────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │     Support Tickets      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │       SQL Database        │
                    └──────────────────────────┘

                    ┌──────────────────────────┐
                    │      Knowledge Base       │
                    │          + RAG             │
                    └──────────────────────────┘
🧠 Agent System

The system uses a central support orchestrator that coordinates specialized components:

Component	Responsibility
Intent Agent	Identifies the customer's request
Sentiment Agent	Detects customer sentiment
Order Agent	Handles order status and tracking
Payment Agent	Handles payment information
Return Workflow	Processes return requests
Cancellation Agent	Handles order cancellation
Ticket Agent	Creates and retrieves support tickets
Knowledge Agent	Answers policy and company questions using RAG
Troubleshooting Agent	Handles technical/problem-solving requests
Escalation Agent	Determines when human support is required
Support Orchestrator	Coordinates the complete workflow

🔐 Security

Security and customer data isolation are core parts of the system.

Authentication

Customers authenticate using JWT access tokens.

The authenticated customer ID is obtained from the JWT rather than trusting a customer ID supplied by the frontend.

Authorization

Business tools verify that the requested resource belongs to the authenticated customer.

Examples:

Customer 1 cannot access Customer 2's orders.
Customer 1 cannot access Customer 2's payment information.
Customer 1 cannot create returns for Customer 2's orders.
Support tickets are filtered by authenticated customer ID.
Data Isolation

Database queries use the authenticated customer's identity when retrieving customer-specific information.

This prevents cross-customer information leakage.

📚 Retrieval-Augmented Generation

The system uses a company knowledge base to answer policy-related questions.

The RAG workflow allows the agent to:

Receive a customer question.
Identify whether company knowledge is required.
Search the knowledge base.
Retrieve relevant information.
Generate a response using the available documentation.

The system avoids inventing policy details when information is not present in the available documentation.

🧪 Automated Testing

Security-focused automated tests are included using pytest.

Current tests verify:

Customer can access their own order.
Customer cannot access another customer's order.
Customer cannot access another customer's payment.
Customer cannot access another customer's return.
Customer ticket data remains isolated.

Current result:
5 passed

⚙️ Continuous Integration

GitHub Actions automatically runs the test suite when:

Code is pushed to main
A pull request targets main

The CI pipeline:

Checks out the repository.
Sets up Python 3.10.
Installs project dependencies.
Runs the automated tests.
🛠️ Tech Stack
Backend
Python
FastAPI
SQLModel
SQLite
Pydantic
JWT
pwdlib
AI / RAG
OpenAI-compatible API
LangChain
FAISS
Sentence Transformers
Frontend
HTML
CSS
JavaScript
Testing & DevOps
pytest
Git
GitHub
GitHub Actions

📁 Project Structure

Autonomous-Customer-Support-Agent/
│
├── backend/
│   └── app/
│       ├── agents/
│       ├── core/
│       ├── database/
│       ├── models/
│       ├── routers/
│       └── tools/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── knowledge_base/
│
├── tests/
│   └── test_security.py
│
├── vector_store/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

🚦 Running the Project Locally

1. Clone the repository
git clone https://github.com/manya0605/Autonomous-Customer-Support-Agent.git
cd Autonomous-Customer-Support-Agent

2. Create a virtual environment
python -m venv venv

3. Activate the environment
Windows PowerShell:
.\venv\Scripts\Activate.ps1

4. Install dependencies
pip install -r requirements.txt

5. Configure environment variables
Create a .env file in the project root.
Use .env.example as a reference:
OPENROUTER_API_KEY=paste your key here
JWT_SECRET_KEY=paste your key here
Add your own local values.
Never commit .env or API keys to GitHub.

6. Start the backend
From the project root:
uvicorn backend.app.main:app --reload
The API will be available through the FastAPI server.

7. Start the frontend
Open another PowerShell window:
cd frontend
python -m http.server 5500
Then open:
http://127.0.0.1:5500

🧪 Running Tests

Run:
.\venv\Scripts\python.exe -m pytest tests -v
Expected result:
5 passed

🔑 API Authentication

Protected API endpoints require a JWT bearer token.
Example:
Authorization: Bearer <access_token>
The server validates the token and derives the authenticated customer identity from it.

## 📸 Project Overview

![Project Overview](screenshots/project-overview.png)
## 🏗️ System Architecture
![System Architecture](screenshots/architecture.png)

🎯 Project Goals

This project demonstrates how autonomous AI agents can be combined with traditional backend systems to build a secure customer support platform.

The main focus areas are:

Autonomous task routing
Tool-based agent execution
Retrieval-augmented generation
Secure API design
Customer data isolation
Automated business workflows
Human escalation
Automated testing
Continuous integration

👨‍💻 Author

Manya M V

GitHub:
https://github.com/manya0605
