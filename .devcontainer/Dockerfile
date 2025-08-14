# Devcontainer for EHCP AutoGen project
FROM mcr.microsoft.com/devcontainers/python:3.11

# System dependencies (add any PDF libs / build deps if needed later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest only after deps to leverage layer caching
COPY . .

ENV PYTHONUNBUFFERED=1
