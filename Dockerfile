FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_rag.txt .
RUN pip install --no-cache-dir -r requirements_rag.txt

# Copy application code
COPY . .

# Build index during build time (optional, or at runtime)
# We can run it here so the image has the DB pre-built
RUN python build_index.py

# Expose Gradio port
EXPOSE 7860

# Run the app
CMD ["python", "app.py"]
