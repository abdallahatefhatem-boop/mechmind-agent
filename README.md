# MechMind - Engineering Agent ⚙️🤖

MechMind is a highly specialized, intelligent AI agent designed specifically for mechanical engineering. It acts as an automated engineering assistant capable of understanding complex mechanical problems, selecting the correct engineering equations, performing accurate calculations without hallucination, and formatting the results into detailed, human-readable explanations.

The system is built on top of **LangGraph**, **FastAPI**, and **Streamlit** to create a multi-agent pipeline backed by structured LLMs (Groq and Google Gemini) and a PostgreSQL checkpointing system.

---

## 🏗️ System Architecture & Workflow

MechMind is not a simple chat wrapper; it uses a state-machine architecture (LangGraph) to safely route and execute engineering tools.

![LangGraph Architecture](./graph.png)

### The Agent Pipeline (How it works under the hood)

1. **`extract_problem` (Problem Categorization)**
   The user's query first enters this node. An LLM analyzes the text to determine the broad category of the engineering problem (e.g., `gear_design`, `shaft_design`, `fluid_flow`, or `noproblem` for general chat).

2. **`extract_equation_name` (Parameter Extraction)**
   Based on the categorized problem, the system provides the LLM with specific supported operations. The LLM extracts the exact operation needed (e.g., `shaft_diameter`), the numerical parameters, and their associated physical units.

3. **`chat_node` & `tool_node` (Dynamic Tool Binding)**
   To bypass context token limits (like Groq's 8000 TPM limit) and avoid tool validation errors, MechMind uses a **smart dynamic tool filter**. 
   - It filters the 35+ available engineering tools down to only the relevant ones based on Phase 1 (exact problem_type match) and Phase 2 (fuzzy word-stem match).
   - The LLM acts as the orchestrator, binding to these specific tools and generating actual tool calls (`tool_node` executes them and calculates exact physics safely in Python).

4. **`format_output_node` (Structured Formatting)**
   Once calculations are done, the message history is "sanitized" (historical tool calls are converted to plain text) to prevent strict API validation errors. Finally, `PydanticOutputParser` forces the LLM to output a perfectly structured JSON payload containing:
   - Extracted results.
   - Validation warnings (e.g., "Assumed 100% efficiency").
   - A beautifully formatted Markdown explanation showing formulas, substitutions, and results.

---

## 🚀 Quick Start (Docker Compose) - Recommended

The most reliable and conflict-free way to run the entire system (Frontend, Backend, and Database) is using Docker Compose.

### Prerequisites
- Docker and Docker Compose installed.
- Valid API keys for the LLMs.

### 1. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=gsk_your_groq_key_here
GOOGLE_API_KEY=AIza_your_google_key_here
```

### 2. Run the Environment
Use the provided Makefile shortcut to build and start all containers in the background:
```bash
make docker-up
```

### 3. Access the Application
- **Frontend (MechMind UI)**: [http://localhost:8501](http://localhost:8501)
- **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop the Environment
```bash
make docker-down
```

---

## 💻 Local Development Setup (Standalone Virtual Environment)

If you are a developer and want to run the code locally in a completely isolated environment independent of Docker, we use **`uv`**, the ultra-fast Python package manager written in Rust. This guarantees your system Python remains clean.

### Prerequisites
- Python 3.12+
- PostgreSQL server running locally (or via Docker).

### 1. Create Isolated Environment & Install Dependencies
Run the following command to create a standalone virtual environment (`.venv`) and install all dependencies exactly as defined in the lock file:
```bash
make setup
```
*(This uses `uv venv` and `uv sync` to perfectly replicate the environment in milliseconds).*

### 2. Activate the Environment
Before running custom scripts or developing, you can activate the isolated environment:
```bash
source .venv/bin/activate
```

### 2. Start the Database
If you don't have Postgres installed on your machine, you can spin up just the database container:
```bash
make db-setup
```

### 3. Start the Backend API
In your first terminal tab, run the FastAPI backend:
```bash
make run-backend
```
*The backend connects to Postgres to save the state of every conversation (Checkpointing), allowing the LLM to remember the context of multi-turn interactions.*

### 4. Start the Frontend UI
In a second terminal tab, launch Streamlit:
```bash
make run-frontend
```

---

## 🧰 Environment Variables Reference

| Variable | Description | Default / Example |
|---|---|---|
| `DB_URI` | Postgres connection string for LangGraph checkpoints. | `postgresql://postgres:postgres@localhost:5432/engineering_db` |
| `API_URL` | The URL the Streamlit frontend uses to talk to FastAPI. | `http://backend:8000/api/v1` (in Docker) |
| `GROQ_API_KEY` | API Key for Groq's blazing fast LLaMA models. | `gsk_...` |
| `GOOGLE_API_KEY` | API Key for Google's Gemini models. | `AIza...` |

---

## 🧪 Testing

We use `pytest` alongside FastAPI's `TestClient` to ensure system stability. The test suite checks if the API routes mount correctly and if the schema validation works.

To run the test suite locally:
```bash
make test
```

---

## 🛠️ CI/CD (GitHub Actions)

MechMind includes an automated Continuous Integration (CI) pipeline. 
When you push code to `main` or open a Pull Request, GitHub Actions automatically executes the `.github/workflows/ci.yml` pipeline:
1. Spawns an Ubuntu runner.
2. Initializes a PostgreSQL service container (required for tests).
3. Installs `uv` and downloads all dependencies instantly.
4. Executes the `pytest` test suite.

This ensures that broken code (like syntax errors or missing dependencies) never reaches production.

---

## 📂 Project Structure Dive

- **`/src/main.py`**: The FastAPI application entry point. Mounts the router and serves the API.
- **`/src/pipeline/Workflow.py`**: The brain of the application. Contains all the LangGraph nodes (`chat_node`, `tool_node`, `format_output_node`) and the dynamic tool filtering logic.
- **`/src/pipeline/graph.py`**: Defines the edges and conditional routing of the LangGraph state machine.
- **`/src/Backend/engineering_tools/`**: A library of pure Python functions containing all physics equations (from thermodynamics to beam stresses).
- **`/config/Prompts.yaml`**: The critical prompt engineering files that dictate how the LLM behaves and formats its Markdown output.
- **`/tests/`**: Unit tests to ensure API stability.
