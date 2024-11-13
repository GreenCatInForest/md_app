# Use an official Python runtime as a parent image
FROM python:3.12-slim
LABEL maintainer="cambridgelogic.com"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV MPLCONFIGDIR=/code/.config/matplotlib

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    ca-certificates \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*
    

# Install Node.js for Tailwind CSS
ARG NODE_MAJOR=20
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g tailwindcss postcss autoprefixer && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man && \
    apt-get clean

# **Copy the application code first**
COPY . /code/


# Set working directory for Node.js dependencies
WORKDIR /code/tailwind_app/static_src

# Install Node.js dependencies
RUN npm install

# Return to the base directory
WORKDIR /code

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy wait-for-it.sh and make it executable
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Define build arguments
ARG SECRET_KEY
ARG CELERY_BROKER_URL
ARG CELERY_RESULT_BACKEND
ARG REDIS_HOST_URL
ARG DB_NAME
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG DB_HOST
ARG DB_PORT

# Set environment variables from build args
ENV SECRET_KEY=${SECRET_KEY}
ENV CELERY_BROKER_URL=${CELERY_BROKER_URL}
ENV CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
ENV REDIS_HOST_URL=${REDIS_HOST_URL}
ENV DB_NAME=${DB_NAME}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_PORT=${DB_PORT}

RUN SECRET_KEY=${SECRET_KEY} python manage.py tailwind install --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py tailwind build --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py collectstatic --no-input


# Expose port
EXPOSE 1091

# Define the default command to run the application
CMD ["gunicorn", "md_app.wsgi:application", "--bind", "0.0.0.0:1091"]
