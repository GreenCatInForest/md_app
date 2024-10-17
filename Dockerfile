FROM python:3.12-slim
LABEL maintainer="cambridgelogic.com"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1 
 # Install system dependencies
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

# Arguments for user and group IDs
ARG USER_ID=1002
ARG GROUP_ID=1002

# Create a system group and user with specific UID and GID
RUN addgroup --gid $GROUP_ID appgroup && \
    adduser --disabled-password --no-create-home --uid $USER_ID --gid $GROUP_ID appuser
    
# Install Node.js for Tailwind CSS
ARG NODE_MAJOR=20
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man && \
    apt-get clean

# Copy and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories and set ownership
RUN mkdir -p /code/imgs && \
    mkdir -p /code/.config/matplotlib && \
    mkdir -p /code/staticfiles/admin/img && \
    chown -R appuser:appgroup /code/imgs /code/.config/matplotlib /code/staticfiles

# Copy wait-for-it.sh and make it executable
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Copy the rest of the application code
COPY . /code/


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

# Install Tailwind CSS dependencies and build CSS
RUN SECRET_KEY=${SECRET_KEY} python manage.py tailwind install --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py tailwind build --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py collectstatic --no-input

# Expose port
EXPOSE 1091


# Change ownership of the project directory
RUN chown -R appuser:appgroup /code

# Switch to the non-root user
USER appuser

# Define the default command to run the application
CMD ["gunicorn", "md_app.wsgi:application", "--bind", "0.0.0.0:1091"]