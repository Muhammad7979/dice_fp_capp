# Dockerfile
FROM python:3.11-slim

WORKDIR /client-app

# Install system dependencies and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        ca-certificates \
        curl \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Copy client app
COPY /app /client-app/

# Install required Python packages
RUN pip install --no-cache-dir flask requests

# Folder to save received data
RUN mkdir -p /clientdata

# Expose port 5001
EXPOSE 5001

# Run Flask client app
CMD ["python", "client.py"]