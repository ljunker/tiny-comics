FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
 && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --frozen --python 3.12

COPY app.py ./app.py
COPY static ./static

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:${PATH}" \
	PYTHONUNBUFFERED=1 \
	PORT=5000

VOLUME ["/app/static/comics"]

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/').read()" || exit 1

CMD ["python", "app.py"]
