.PHONY: setup test run-backend run-frontend run-all docker-up docker-down

# Create an isolated standalone virtual environment and install dependencies
setup:
	uv venv
	uv sync

# Run the test suite
test:
	uv pip install pytest httpx
	PYTHONPATH=. uv run pytest tests/ -v

# Run the FastAPI backend locally
run-backend:
	uv run uvicorn src.main:app --reload

# Run the Streamlit frontend locally
run-frontend:
	uv run streamlit run src/ui/app.py

# Docker Compose commands
docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down -v

# Run migrations or db setup (if applicable)
db-setup:
	docker-compose up -d db
