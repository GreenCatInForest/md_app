FROM python:3-slim
LABEL maintainer="cambridgelogic.com"

ENV PYTHONUNBUFFERED 1   
 
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt-get update && \
apt-get install -y curl gnupg && \
curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
apt-get install -y nodejs && \
# Verify installation
node -v && \
npm -v && \
# Clean up the cache by removing temporary files
apt-get clean && \
rm -rf /var/lib/apt/lists/*

COPY . /code/