# ⚙️ MechMind - The Intelligent Mechanical Engineering Agent 🤖

[![CI/CD Pipeline](https://github.com/abdallahatefhatem-boop/mechmind-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/abdallahatefhatem-boop/mechmind-agent/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.142.2-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.65.0-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2.12-orange.svg)](https://langchain.com)

Welcome to **MechMind**, a highly specialized AI agent designed specifically for **Mechanical Engineers, Students, and Researchers**. 

Large Language Models (LLMs) are notoriously bad at math and physics calculations. They hallucinate numbers and mess up formulas. **MechMind solves this problem.** By acting as an orchestrator, the AI understands your natural language engineering problem, extracts the physics parameters, and delegates the actual heavy mathematical lifting to **pure Python deterministic tools**. The result is a 100% accurate calculation wrapped in a beautiful, human-readable explanation.

---

## 🌟 Key Features

1. **Deterministic Accuracy**: The AI doesn't "guess" the math. It parses your query and calls strict Python functions (e.g., `calculate_beam_deflection(force, length)`).
2. **LangGraph State Machine**: Uses a state-of-the-art multi-agent pipeline to route your problem through distinct stages (Categorization ➔ Parameter Extraction ➔ Tool Execution ➔ Formatting).
3. **Dynamic Tool Filtering**: To avoid context-window limits, the engine dynamically binds only the relevant engineering tools out of a library of 35+ specialist tools.
4. **Persistent Memory**: Backed by PostgreSQL, the agent remembers previous calculations in your thread, allowing for multi-step engineering design processes.
5. **Human-Readable Outputs**: Forces the LLM to output beautifully formatted Markdown with "Given Data", "Formulas Used", "Step-by-step Substitution", and "Engineering Warnings/Assumptions".

---

## 🛠️ Supported Engineering Domains

MechMind is equipped with a vast arsenal of mechanical engineering formulas under the hood. It can solve problems in:

- **Solid Mechanics & Statics**: Beam stresses, beam deflection, column buckling (Euler's), stress/strain analysis.
- **Machine Design**: Shaft design (bending & torsion), gear design (ratio, speed, torque), bearing life calculation, spring design, bolt strength & shear.
- **Fluid Mechanics**: Fluid flow in pipes (Reynolds number, pressure drop), pump power, and hydraulic head.
- **Thermodynamics & Heat Transfer**: Conduction, convection, radiation, thermal expansion, basic HVAC cooling/heating loads.
- **General Mechanics**: Force, mass, acceleration, torque, work, energy, power, and unit conversions.

*(If you ask it a non-engineering question, like "Hello", the system intelligently bypasses the math tools and chats with you naturally).*

---

## 🏗️ How The Engine Works (Deep Dive)

The backend is entirely powered by **LangGraph**, creating a loop of nodes that process your query step-by-step.

![LangGraph Architecture](./graph.png)

1. **`extract_problem` Node (The Classifier)**: 
   Your query goes here first. A fast LLM categorizes the text (e.g., identifies it as a `gear_design` problem).
2. **`extract_equation_name` Node (The Extractor)**: 
   Knowing it's a gear problem, the LLM is restricted to gear-related operations. It extracts the exact parameters (like `15 kW power`, `1200 RPM`) and maps them to standard units.
3. **`chat_node` & `tool_node` (The Orchestrator & Executor)**: 
   The system filters out unrelated tools (to save API tokens) and binds only the relevant Python tools. The LLM then generates a "Tool Call", which executes pure Python code. The exact mathematical result is returned to the state.
4. **`format_output_node` (The Explainer)**: 
   The historical tool calls are "sanitized" (to prevent API validation errors). A final LLM pass uses `PydanticOutputParser` to inject the raw Python output into a beautiful Markdown JSON schema, providing you with a step-by-step tutorial of how the number was calculated.

---

## 🚀 Quick Start (Docker Compose) - The Easiest Way

The repository includes a production-ready `docker-compose.yml` that spins up the Frontend, Backend, and Database simultaneously.

### 1. Configure API Keys
Create a `.env` file in the root directory:
```env
# Required for the LLM to work
GROQ_API_KEY=gsk_your_groq_api_key_here
GOOGLE_API_KEY=AIza_your_google_api_key_here
```

### 2. Launch the Environment
Make sure you have Docker installed, then run:
```bash
make docker-up
```
*This will build the images using `uv` for blazing-fast dependency installation and start 3 containers: `db`, `backend`, and `frontend`.*

### 3. Access the App
- **MechMind UI (Streamlit)**: [http://localhost:8501](http://localhost:8501)
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop the Environment
```bash
make docker-down
```

---

## 💻 Local Development (Standalone Environment)

If you wish to contribute to the code or run it locally without Docker, we use **`uv`** (an ultra-fast Python package manager written in Rust).

### Prerequisites
- Python 3.12+
- A running PostgreSQL instance (or you can use Docker just for the DB via `make db-setup`).

### 1. Setup Isolated Virtual Environment
```bash
make setup
```
*This runs `uv venv` and `uv sync`, creating a `.venv` directory and perfectly replicating the `uv.lock` dependencies in milliseconds.*

### 2. Activate Environment
```bash
source .venv/bin/activate
```

### 3. Run Backend (FastAPI)
```bash
make run-backend
```

### 4. Run Frontend (Streamlit)
```bash
make run-frontend
```

---

## 🧪 Testing & CI/CD

We take code reliability seriously. The project uses `pytest` to validate the API endpoints and routing logic.

### Run tests locally:
```bash
make test
```

### GitHub Actions (CI Pipeline)
Every Push or Pull Request to the `main` branch triggers our automated CI pipeline (defined in `.github/workflows/ci.yml`). 
The pipeline automatically:
1. Provisions an Ubuntu runner.
2. Starts a PostgreSQL service.
3. Installs `uv` and dependencies.
4. Mounts the project with dummy API keys.
5. Executes the `pytest` suite.
**No broken code gets merged!**

---

## ⚙️ Environment Variables Reference

| Variable | Description | Example |
|---|---|---|
| `DB_URI` | PostgreSQL connection string for saving agent memory. | `postgresql://postgres:postgres@localhost:5432/engineering_db` |
| `API_URL` | The URL the Streamlit frontend points to. | `http://backend:8000/api/v1` |
| `GROQ_API_KEY` | Key for Groq's high-speed inference models. | `gsk_...` |
| `GOOGLE_API_KEY` | Key for Google's Gemini models. | `AIza...` |

---

## 🤝 Contributing

We welcome contributions! If you want to add a new mechanical engineering formula:
1. Create a new Python tool in `src/Backend/engineering_tools/`.
2. Add its schema to the prompt templates in `config/Prompts.yaml`.
3. Register the tool in `src/pipeline/Workflow.py` (`TOOL_MAPPING`).
4. Write tests and open a Pull Request!
