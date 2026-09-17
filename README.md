Autonomous Customer Support Agent



An AI-powered customer support system that autonomously understands customer requests, routes them to specialized agents, uses business tools and knowledge-base retrieval, enforces customer-level authorization, maintains conversation history, and escalates appropriate cases to human support.



Overview



The Autonomous Customer Support Agent is a full-stack AI customer-support application built with a Python/FastAPI backend and a browser-based frontend.



Instead of relying on a single chatbot response, the system uses an orchestration layer that analyzes each customer request and routes it to the appropriate specialized agent.



The system supports:



\- Customer registration and login

\- JWT-based authentication

\- Customer-specific data isolation

\- Order status and tracking

\- Order cancellation

\- Return requests

\- Payment status

\- Support ticket creation and retrieval

\- Knowledge-base and RAG-based policy responses

\- Troubleshooting workflows

\- Sentiment analysis

\- Human-support escalation

\- Conversation history

\- Audit logging



Architecture



Customer

&#x20;  │

&#x20;  ▼

Frontend

&#x20;  │

&#x20;  ▼

FastAPI API

&#x20;  │

&#x20;  ▼

Support Orchestrator

&#x20;  │

&#x20;  ├── Intent Agent

&#x20;  ├── Sentiment Agent

&#x20;  ├── Escalation Agent

&#x20;  │

&#x20;  ├── Order Agent

&#x20;  ├── Payment Agent

&#x20;  ├── Ticket Agent

&#x20;  ├── Knowledge Agent

&#x20;  └── Troubleshooting Agent

&#x20;          │

&#x20;          ▼

&#x20;       Tools Layer

&#x20;          │

&#x20;          ├── Order Tools

&#x20;          ├── Payment Tools

&#x20;          ├── Return Tools

&#x20;          ├── Refund Tools

&#x20;          ├── Ticket Tools

&#x20;          ├── RAG Tools

&#x20;          ├── Memory Tools

&#x20;          └── Audit Tools

&#x20;                 │

&#x20;                 ▼

&#x20;            Database



Key Features



🔐 Authentication and Authorization



The application uses JWT-based authentication.



Authenticated customer identity is obtained from the JWT rather than from the chat request body.



Customer-specific resources are protected so that a customer cannot access another customer's:



\- Orders

\- Payment information

\- Return information

\- Support tickets



🤖 Multi-Agent Support



The system uses specialized agents for different support responsibilities.



Agent| Responsibility

Intent Agent| Identifies the customer's request

Sentiment Agent| Detects customer sentiment

Escalation Agent| Determines whether human support is required

Order Agent| Handles order status and tracking

Payment Agent| Handles payment-related requests

Ticket Agent| Creates and retrieves support tickets

Knowledge Agent| Answers policy/product/FAQ questions

Troubleshooting Agent| Handles troubleshooting workflows

Support Orchestrator| Coordinates the complete workflow



📦 Order Support



Customers can ask about their orders, including:



\- Order status

\- Order tracking

\- Order cancellation



The system verifies order ownership before returning order information or performing protected actions.



↩️ Returns and Refunds



The system supports return workflows with:



\- Order ownership validation

\- Return eligibility checks

\- Existing-return detection

\- Duplicate return prevention

\- Return request creation

\- Return status retrieval



💳 Payment Support



Customers can retrieve payment information associated with their own orders.



Payment access is protected using customer ownership validation.



🎫 Support Tickets



The system can:



\- Create support tickets

\- Detect existing open tickets

\- Retrieve a customer's support tickets

\- Associate tickets with the authenticated customer

\- Create tickets during human escalation



📚 Knowledge Base and RAG



The application uses a knowledge base containing company policies and product/troubleshooting information.



Knowledge-related questions are answered using retrieved documentation rather than relying only on generated responses.



Example knowledge areas include:



\- Return policy

\- Refund policy

\- Cancellation policy

\- Shipping policy

\- FAQs

\- Product manual

\- Troubleshooting guides



🧑‍💼 Human Escalation



The system can identify situations that require human support.



When escalation is required, the system can create a support ticket containing the customer's request and relevant context.



💾 Conversation Memory



Customer conversations are stored and associated with the customer and conversation ID.



This allows the system to maintain conversation context while keeping customer histories isolated.



📝 Audit Logging



Important actions and outcomes are recorded through the audit logging system.



This provides traceability for operations such as:



\- Cancellations

\- Returns

\- Support tickets

\- Escalations

\- Authorization-related outcomes



Technology Stack



Backend



\- Python

\- FastAPI

\- SQLModel

\- SQLite

\- JWT authentication

\- Password hashing

\- RAG / knowledge retrieval



Frontend



\- HTML

\- CSS

\- JavaScript



AI Architecture



\- Multi-agent orchestration

\- Intent classification

\- Sentiment analysis

\- Escalation decision logic

\- Tool-based actions

\- Knowledge-base retrieval

\- Conversation memory



Project Structure



Autonomous-Customer-Support-Agent/

│

├── backend/

│   └── app/

│       ├── agents/

│       ├── core/

│       ├── database/

│       ├── models/

│       ├── rag/

│       ├── routers/

│       └── tools/

│

├── frontend/

│   ├── index.html

│   ├── style.css

│   └── app.js

│

├── knowledge\_base/

│   ├── cancellation\_policy.txt

│   ├── faq.txt

│   ├── product\_manual.txt

│   ├── refund\_policy.txt

│   ├── return\_policy.txt

│   ├── shipping\_policy.txt

│   └── troubleshooting\_\*.txt

│

├── tests/

├── data/

├── vector\_store/

├── .gitignore

└── README.md



Running the Project



1\. Clone the repository



git clone https://github.com/manya0605/Autonomous-Customer-Support-Agent.git

cd Autonomous-Customer-Support-Agent



2\. Create and activate a virtual environment



Windows PowerShell:



python -m venv venv

.\\venv\\Scripts\\Activate.ps1


### Environment Variables

Create a local .env file from the provided template:

```powershell
copy .env.example .env



3\. Install dependencies



pip install -r requirements.txt



If the project uses a different dependency file in your environment, follow that file instead.



4\. Configure environment variables



Create a ".env" file in the project root and configure the required environment variables.



Do not commit ".env" to GitHub.



5\. Start the backend



From the project root:



uvicorn backend.app.main:app --reload



The API will be available at:



http://127.0.0.1:8000



Swagger API documentation:



http://127.0.0.1:8000/docs



6\. Start the frontend



Open another PowerShell window:



cd frontend

python -m http.server 5500



Then open:



http://127.0.0.1:5500



Security



The project includes several security controls:



\- JWT authentication

\- Password hashing

\- Authenticated customer identity

\- Customer-level resource ownership checks

\- Protected agent API

\- CORS configuration

\- Environment-variable based secret configuration

\- Exclusion of secrets and local database files through ".gitignore"



Tested Workflows



The following workflows have been tested through the application:



\- Customer registration/login

\- Authenticated agent access

\- Unauthorized agent access

\- Own-order status lookup

\- Cross-customer order protection

\- Return creation

\- Duplicate return prevention

\- Cross-customer return protection

\- Payment status lookup

\- Cross-customer payment protection

\- Support ticket creation

\- Customer-isolated ticket retrieval

\- Knowledge-base/RAG responses

\- General conversation

\- Human-support escalation



Example Requests



What is the status of order 1?



I want to return order 1



What is the payment status of order 1?



Show me my support tickets



What is your return policy?



I want to speak to a human support representative



Project Goals



The goal of this project is to demonstrate how an autonomous AI customer-support system can combine:



\- AI reasoning

\- Multi-agent orchestration

\- Tool execution

\- Retrieval-augmented knowledge

\- Authentication

\- Authorization

\- Persistent conversation memory

\- Business workflows

\- Human escalation

\- Auditability



into a single end-to-end customer-support application.



Future Improvements



Potential future improvements include:



\- Production-grade database deployment

\- More comprehensive automated tests

\- Improved observability and monitoring

\- Background job processing

\- Role-based support-agent access

\- Production deployment

\- More advanced retrieval and evaluation

\- Automated CI/CD

\- Additional customer-support workflows



Author



Manya M V



GitHub:

https://github.com/manya0605/Autonomous-Customer-Support-Agent

