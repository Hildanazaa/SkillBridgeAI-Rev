# Gunakan base image Python slim untuk efisiensi size container
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Install dependensi sistem yang diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file terlebih dahulu untuk memanfaatkan caching Docker layer
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer model agar ter-cache di dalam Docker image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy seluruh file aplikasi ke dalam container
COPY . .

# Set environment variables untuk production run
ENV PYTHONUNBUFFERED=1

# Expose port (default 8000, atau otomatis membaca port dari server host seperti Render/Railway/HuggingFace)
EXPOSE 8000

# Jalankan server FastAPI dengan Uvicorn
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
