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
COPY config.py .

# Create necessary directories
RUN mkdir -p Results/visualizations Results/reports Results/logs

# Expose port that Cloud Run expects
EXPOSE 8080

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
