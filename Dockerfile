# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /app/

# Create media directory in case it doesn't exist
RUN mkdir -p /app/media /app/staticfiles

# Run collectstatic to compile all static files into staticfiles directory
# Set dummy environment variables to allow collectstatic to run without real credentials
RUN SECRET_KEY=dummy-secret-key-for-collectstatic \
    DEBUG=False \
    python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Daphne ASGI server
CMD daphne -b 0.0.0.0 -p $PORT skill_currency.asgi:application
