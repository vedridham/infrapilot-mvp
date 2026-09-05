# InfraPilot

An evidence-backed AI incident investigator for database-backed applications.

InfraPilot helps engineering teams investigate why an application is slow or failing by correlating application, database, deployment, and diagnostic evidence into a safe, human-approved remediation recommendation.

## Problem

When a production application becomes slow or starts failing, the root cause can be difficult to identify.

Engineers often need to inspect:

- Application latency and errors
- Database query performance
- Database CPU usage
- Query execution plans
- Recent deployments
- Deployment changes

These signals are usually investigated separately.

InfraPilot brings these signals together and produces an evidence-backed incident diagnosis.

## MVP Demo Scenario

InfraPilot demonstrates a controlled database performance incident:

1. A new order-history release is deployed.
2. The application starts using a query without a usable `(user_id, created_at)` index.
3. PostgreSQL performs a sequential scan.
4. Database query latency increases.
5. Database CPU usage increases.
6. Application latency and error rate increase.
7. InfraPilot correlates the evidence.
8. AI produces a probable cause, confidence, blast radius, and remediation.
9. A human reviews and approves the recommended action.
10. The approval is recorded in an audit log.

InfraPilot does **not** execute uncontrolled SQL or automatically perform destructive remediation.

## Architecture

```text
                    ┌─────────────────────┐
                    │      React UI       │
                    │ Incident Dashboard  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │ Diagnostics │  │ Investigator│  │ AI Diagnosis│
       └──────┬──────┘  └──────┬──────┘  └─────────────┘
              │                │
              └────────────────┘
                       │
                       ▼
                ┌───────────────┐
                │  PostgreSQL   │
                │ Incident Data │
                └───────────────┘

Key Features
Evidence-backed incident investigation
Read-only database diagnostics
Slow query detection
PostgreSQL query plan analysis
Recent deployment correlation
AI-generated diagnosis
Confidence and blast-radius assessment
Human approval workflow
Audit logging
No uncontrolled SQL execution
Technology Stack
Backend
Python
FastAPI
SQLAlchemy
PostgreSQL
Frontend
React
Vite
Recharts
CSS
Infrastructure
Docker
Docker Compose
Git
GitHub
Diagnostic Tools

The MVP provides three read-only diagnostic tools:

get_top_slow_queries
get_query_plan
get_recent_deployments

These tools provide structured evidence to the investigation workflow.

AI Diagnosis

The investigation produces:

Probable cause
Confidence
Evidence
Blast radius
Recommended remediation
Rollback plan

The AI separates observed evidence from its diagnosis instead of presenting unsupported conclusions as facts.

Human Approval

InfraPilot follows a human-in-the-loop approach.

The system recommends an action, but the user must review and approve it.

The current approval endpoint records the approval in an audit log. It does not execute rollback SQL or other uncontrolled database operations.

Security

Security is a core part of the MVP:

Database credentials are stored in local .env.
.env is excluded from Git.
.env.example contains placeholder credentials only.
Frontend does not receive database credentials.
Diagnostic database operations are read-only.
No generic SQL execution endpoint is exposed.
Remediation requires human approval.
Approval creates an audit record but does not execute destructive actions.
PostgreSQL is bound to 127.0.0.1 in Docker Compose.
API Endpoints
Endpoint	Method	Purpose
/health	GET	API health check
/api/investigate	GET	Run incident investigation
/api/diagnostics/slow-queries	GET	Retrieve slow query evidence
/api/diagnostics/query-plan	GET	Retrieve query plan
/api/diagnostics/deployments	GET	Retrieve recent deployments
/api/incidents/{incident_id}/approve	POST	Record human approval
/api/incidents/{incident_id}/audit-logs	GET	Retrieve approval history
Running Locally
Prerequisites
Python
Node.js
Docker Desktop
Git
1. Clone the repository
git clone https://github.com/vedridham/infrapilot-mvp.git
cd infrapilot-mvp
2. Configure environment variables

Create a local .env file using .env.example.

Never commit .env to Git.

3. Start PostgreSQL
docker compose up -d
4. Start the backend
cd backend
uvicorn main:app --reload

Backend:

http://127.0.0.1:8000
5. Start the frontend

Open another terminal:

cd frontend
npm install
npm run dev

Frontend:

http://localhost:5173
Demo Flow
Application slowdown
        |
        v
Incident investigation
        |
        v
Slow query evidence
        |
        v
Query execution plan
        |
        v
Recent deployment
        |
        v
AI diagnosis
        |
        v
Confidence + blast radius
        |
        v
Recommended remediation
        |
        v
Human approval
        |
        v
Audit log
Project Status

MVP complete and ready for demonstration.

The project focuses on a small, explainable, and secure incident-investigation workflow instead of uncontrolled automated remediation.

Future Scope

1.Lock and deadlock diagnostics
2.Connection-pool investigation
3.Long-running transaction detection
4.Before/after deployment comparison
5.Application log correlation
6.Distributed trace correlation
7.Authentication and role-based access control
8.More advanced incident detection
9.Staging remediation validation


License

MIT License
