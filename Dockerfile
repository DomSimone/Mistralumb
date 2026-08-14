# Use the full Python image (not slim) to avoid building issues with llama-cpp
FROM python:3.11-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install only necessary extra dependencies
# We use a retry loop for apt-get update to handle transient network issues
RUN apt-get update || (sleep 5 && apt-get update) && \
    apt-get install -y --no-install-recommends \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy the application source code
COPY fastapi_server.py .
COPY umbuzo_chatbot.py .
COPY rag_system.py .
COPY country_vectorizer.py .
COPY open_source_retrieval.py .
COPY cdx_african_content.py .
COPY data_generator.py .
COPY run_server.py .
COPY Mbuzo_Logo.png .
COPY umbuzo_conversation.json .

# Copy the frontend directory
COPY frontend .frontend/

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run the application
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
