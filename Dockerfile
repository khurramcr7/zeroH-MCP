FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ONEXI_API_URL="https://onexi.tech/api"

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY zeroh_mcp ./zeroh_mcp

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "zeroh_mcp.server"]
