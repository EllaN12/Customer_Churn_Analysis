# Dockerfile for Streamlit Dashboard on Google Cloud Run

# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY streamlit_dashboard.py .

# Expose default port (Cloud Run overrides via the $PORT env var at runtime)
EXPOSE 8080

# Set environment variables for Streamlit
ENV PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check (python urllib — python:3.9-slim has no curl)
HEALTHCHECK CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:%s/_stcore/health' % os.environ.get('PORT','8080'))" || exit 1

# Run Streamlit app — bind to the port Cloud Run provides
CMD streamlit run streamlit_dashboard.py --server.port=${PORT:-8080} --server.address=0.0.0.0
