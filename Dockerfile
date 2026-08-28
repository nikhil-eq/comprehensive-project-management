FROM python:3.11-slim

WORKDIR /app

# Install system deps if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# HF Spaces requires port 7860
EXPOSE 7860

# Run Solara
CMD ["solara", "run", "app.py", "--port=7860", "--host=0.0.0.0", "--no-open"]