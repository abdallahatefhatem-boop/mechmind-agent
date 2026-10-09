FROM python:3.12-slim
WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copy source code
COPY . .

# Put the virtual environment in PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000 8501
