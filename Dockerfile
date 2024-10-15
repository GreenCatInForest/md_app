# Stage 1: Build Stage
FROM python:3.11-slim AS build

LABEL maintainer="cambridgelogic.com"

# Prevents Python from writing pyc files to disk and buffers stdout and stderr
ENV PYTHONUNBUFFERED=1 

WORKDIR /code

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \          
        libpq-dev \                
        python3-dev \              
        curl \                    
        gnupg \                    
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt /code/
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh


RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Node.js
ARG NODE_MAJOR=20

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \         
        curl \                    
        gnupg \                   
    && mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man && \
    apt-get clean

# Copy application code
COPY . /code/



# Install Tailwind and collect static files
RUN SECRET_KEY=${SECRET_KEY} python manage.py tailwind install --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py tailwind build --no-input && \
    SECRET_KEY=${SECRET_KEY} python manage.py collectstatic --no-input

# Stage 2: Production Stage
FROM python:3.11-slim

LABEL maintainer="cambridgelogic.com"

ENV PYTHONUNBUFFERED=1 

WORKDIR /code

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \                  
        nodejs \                  
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code from build stage
COPY --from=build /code /code

EXPOSE 1091

CMD ["gunicorn", "md_app.wsgi:application", "--bind", "0.0.0.0:1091"]