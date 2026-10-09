FROM python:3.12-slim

WORKDIR /app

# Build tools needed by some wheels; removed in the same layer to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --without dev

COPY . .

EXPOSE 8000

# The app is built by a factory so env is validated and the lifespan runs.
CMD ["uvicorn", "--factory", "main:create_app", "--host", "0.0.0.0", "--port", "8000"]
