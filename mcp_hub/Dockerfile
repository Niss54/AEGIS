FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY mcp_hub/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_hub /app/mcp_hub

ENV PYTHONPATH=/app
EXPOSE 8001

CMD ["uvicorn", "mcp_hub.hub:app", "--host", "0.0.0.0", "--port", "8001"]
