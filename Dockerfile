FROM python:3.11-slim

WORKDIR /app

# Install dependencies required for PDF, DOCX processing
RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    libmagic1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir \
    beautifulsoup4 \
    email-validator \
    flask \
    flask-sqlalchemy \
    gunicorn \
    markdown \
    psycopg2-binary \
    pypdf2 \
    python-docx \
    pytesseract \
    python-pptx \
    werkzeug \
    openpyxl \
    pandas

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]