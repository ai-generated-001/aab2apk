FROM python:3.11-slim

# Install system dependencies (Java JRE for bundletool, curl for downloading bundletool, unzip for extracting APKs)
RUN mkdir -p /usr/share/man/man1 && \
    apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/bin /tmp/aab2apk/uploads /tmp/aab2apk/outputs

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
