FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    streamlit

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports for API and Streamlit UI
EXPOSE 8000
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run the application (API or Streamlit UI based on APP_MODE)
ENV APP_MODE=api
CMD if [ "$APP_MODE" = "streamlit" ]; then \
    streamlit run src/app/demo/streamlit.py --server.port 8501 --server.address 0.0.0.0; \
  else \
    python -m src.api.app; \
  fi 