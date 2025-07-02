# Use Python 3.11.1 slim base image
FROM python:3.11.1-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside container
WORKDIR /app

# Install system dependencies (optional for SQLite)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all your code inside the image
COPY . .

# Run database migrations
RUN python manage.py migrate

# Expose port 8000 for access
EXPOSE 8000

# Run the Django dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
