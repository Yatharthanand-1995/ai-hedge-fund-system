# Use Python 3.11 (App Runner supports 3.11, tested with our system)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for TA-Lib compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib from source (required for technical indicators)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (App Runner will auto-detect)
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8010/health')"

# Start application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8010"]
