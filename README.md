# support_ticket_analyst
A tiny tool that uses a LangGraph-driven agent to analyze and summarize support tickets and store results in Postgres. The project contains a Flask backend, a React frontend, and a simple Postgres schema for persistence.

## Quickstart

Prerequisites
- Docker
- Docker Compose (v1.27+ or compatible)

How to run the whole project
1. (Optional) Rebuild the frontend static bundle locally if you made frontend changes:

```powershell
cd frontend
npm install
npm run build
cd ..
```

2. From the project root (where `docker-compose.yml` lives) start the stack:

```powershell
docker-compose up -d
```

3. Confirm containers are running:

```powershell
docker-compose ps
```

4. View logs if something fails:

```powershell
docker-compose logs -f backend
docker-compose logs -f db
```

Default ports
- Frontend (nginx serving `frontend/build`): http://localhost:3000
- Backend (Flask): http://localhost:5000
- Postgres DB: 5432 (host: localhost, container exposes 5432)

Configuration
- Environment variables can be provided in multiple ways:
	- `docker-compose.yml` currently embeds the minimal DB credentials for local development (POSTGRES_USER=postgres, POSTGRES_PASSWORD=root, POSTGRES_DB=ticket_analyze_db).
	- You can provide a `.env` file in the project root and reference variables via `docker-compose` or expand the compose file to use `${VAR_NAME}` interpolation.
	- For local development you can also export vars in your shell before running compose.

How environment variables are set in this project
- The provided `docker-compose.yml` sets service environment variables in the `environment:` sections of services. This is simple and explicit for the coding test. For production or secure development, prefer a `.env` file (gitignored) and an example `.env.example` committed with placeholder values. Example `.env.example` contents (create at project root):

```
# Example .env.example
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=ticket_analyze_db
FLASK_ENV=production
# LANGGRAPH_KEY=your_api_key_here  # if your LangGraph installation requires an API key
```

How the backend connects to Postgres
- The backend uses `psycopg2` and the helper `get_db_connection()` in `backend/app/models.py`:

	- Host: `db` (the Docker Compose service name)
	- Database: `ticket_analyze_db`
	- User: `postgres`
	- Password: `root`

	When running via Docker Compose, the backend container resolves `db` to the Postgres container on the compose network.

How LangGraph / LLM is configured
- This project uses the `langgraph` Python package. The LangGraph nodes in `backend/app/agent_flow.py` reference model names such as `google/flan-t5-base`.
- There is no repository-stored API key in this code. If your LangGraph installation or chosen model provider requires credentials (API key, service account, etc.), supply them as environment variables (for example `LANGGRAPH_API_KEY` or provider-specific vars). Add them to a `.env` file or your container environment before starting the stack.
- For local testing without an external LLM, LangGraph may provide a stubbed or local model; check the `langgraph` documentation for how to configure a local or mock model.

API Overview

Endpoints (all served by the Flask backend at `/api`):

- POST /api/tickets
	- Purpose: Insert one or more tickets into the database.
	- Request: JSON array of objects, each with at least a `title` string and an optional `description` string.
		- Example request body:
			```json
			[
				{"title": "Login failing", "description": "User cannot log in with SSO"},
				{"title": "Payment error", "description": "Card declined"}
			]
			```
	- Response: 201 Created with a JSON array of created ticket IDs (integers).

- POST /api/analyze
	- Purpose: Run the LangGraph analysis workflow against tickets.
	- Request: JSON object, optional `ticketIds` array specifying which tickets to analyze. If omitted, all tickets are used.
		- Example: `{ "ticketIds": [1, 2, 3] }` or `{}`
	- Response: 201 Created with `{ "output": <workflow return value> }` where `<workflow return value>` is the LangGraph workflow object or its output as returned by `tickets_analyze.run`.

- GET /api/analysis/latest
	- Purpose: Fetch the last analysis run and associated ticket analysis rows.
	- Response: 200 OK with JSON: `{ "analysis_run": <analysis_row_or_null>, "ticket_analysis": [ {"ticket_analysis": <row>}, ... ] }`.

Request/response shapes are intentionally simple; the backend uses psycopg2 and returns basic JSON serializations.

Any non-obvious details
- The backend `routes.py` uses `app` exported from `routes.py` and `FLASK_APP` in `docker-compose.yml` is set to `app.routes:app` so `flask run` can find the Flask app object.
- The Postgres initialization uses `db/create_database.sql` which creates the database and tables on first container launch by mounting it into `/docker-entrypoint-initdb.d/` in the Postgres container.

Architecture Notes

Tech choices
- Backend: Python 3.10 + Flask for a small, lightweight API.
- Database: Postgres for relational persistence (psycopg2 client).
- Agent/LLM orchestration: `langgraph` – lightweight DAG-style orchestrator of model calls.
- Frontend: React (Create React App) served as static files by nginx in the compose setup.

Directory structure (top-level)

```
./backend        # Flask app, Dockerfile, Python requirements
	/app
		__init__.py
		routes.py
		models.py
		agent_flow.py
./db             # DB init SQL
./frontend       # React app; prebuilt static files under frontend/build
docker-compose.yml
README.md
```

How the LangGraph agent is wired to Postgres
- `backend/app/agent_flow.py` builds a LangGraph workflow:
	- `fetch_tickets_node` calls `get_tickets` (from `models.py`) to read rows from Postgres.
	- Summary nodes call LLM models (via LangGraph) to create summaries and assign category/priority.
	- `analyze_tickets` and `create_ticket_analysis` (in `models.py`) are invoked as nodes to insert the overall run and per-ticket analysis rows into Postgres.

Tradeoffs and shortcuts made
- Development-focused defaults: compose embeds DB credentials and uses `flask run` rather than a production WSGI server (gunicorn). These choices prioritize simplicity and fast iteration over production hardening.
- Frontend is served by mounting `frontend/build` into nginx instead of building a dedicated frontend image; this keeps the compose file small but assumes `frontend/build` exists.
- No migrations: the SQL schema is applied via a one-shot SQL script mounted into the Postgres init folder. For production, a migration tool (Alembic/flyway) would be preferable.
- LangGraph usage is minimal and assumes access to the referenced model names; the implementation uses model names directly (e.g., `google/flan-t5-base`) rather than a provider-agnostic configuration layer.

Next steps / suggestions
- Add a `.env.example` and `.env` (gitignored) with any provider keys (LangGraph/LLM) and DB overrides.
- Replace `flask run` with `gunicorn` in `docker-compose.yml` for a production-like backend.
- Add basic integration tests for the API routes and a small health check endpoint.

## Future Improvements
Here are suggested, scoped improvements that would make the project production-ready and easier to maintain:

- CI / CD: add GitHub Actions (or similar) to run linting, unit tests, and build checks on each PR.
- Tests: add unit tests for API routes and models, and an integration test that boots a test Postgres (or uses a test container) and exercises the full stack.
- Schema migrations: add Alembic to manage database migrations instead of a one-shot SQL file.
- Backend process: use Gunicorn (or uWSGI) with multiple workers and proper logging instead of `flask run`.
- Frontend build: add a Dockerfile for the frontend so Compose can build the image during deployment instead of mounting `frontend/build`.
- Configuration & secrets: move secrets out of `docker-compose.yml` into a `.env` (gitignored) and/or use a secret manager for production.
- Health checks & readiness: add `/health` and `/ready` endpoints and configure them to be used by orchestrators and monitoring.
- Observability: add structured logging, metrics (Prometheus), and basic tracing to measure agent/LLM latency and errors.
- LLM safety & cost controls: add request throttling, token limits, and fallback behavior for model errors; consider a mock mode for development.
- Job/queueing: make long-running LangGraph runs asynchronous (e.g., enqueue to Redis/RQ or Celery) and return a job id for polling.
- Validation and error handling: validate incoming payloads with a schema (pydantic / marshmallow) and return consistent error responses.
- API docs: add OpenAPI/Swagger docs for the backend to make endpoints discoverable and testable.
- DB backups & restores: add scripts and policies for periodic DB backups and restore tests.
- Security: add authentication/authorization for the API endpoints, rate-limiting, and input sanitization.
- Docker image hygiene: pin base images, run containers as non-root, and minimize image layers to reduce attack surface.
- Developer experience: provide `Makefile` / `justfile` shortcuts and a `.env.example` to simplify local setup.

Project Development Summary
Time Spent:
Total Development Time: 3.5 hours

Future Improvements (If More Time Were Available):

Given additional time, the following enhancements and features would be added to improve the robustness, maintainability, and scalability of the application:
1. Configuration Management:
.env File: Store sensitive configurations (e.g., API keys, database credentials, etc.) in a .env file to follow best practices and improve the security and flexibility of the project.
2. Unit Tests:
- API Route Tests: Add unit tests for all API endpoints to ensure the correctness of the routes, inputs, and outputs. This will help in detecting any regressions or issues early.
- Model Tests: Create unit tests for models, especially for functions interacting with the database, to verify that the business logic behaves as expected.
3. Validation and Error Handling:
- Input Validation: Add input validation on API requests to ensure that the inputs meet the required format, reducing the risk of invalid data being processed.
- Error and Exception Handling: Implement centralized error handling to provide consistent error messages and status codes, improving the user experience and making the app more reliable.
4. Authentication:
- API Authentication: Implement authentication mechanisms (e.g., JWT, OAuth2) to secure API endpoints, ensuring that only authorized users can access the sensitive operations.
5. Asynchronous Task Execution:
- Job/Queueing System: Use a task queue (such as Celery or RQ) to make LangGraph-related tasks asynchronous. This would improve the performance and responsiveness of the application by allowing long-running tasks (such as analyzing multiple tickets) to run in the background, rather than blocking the main application thread.



