FROM python:3-slim
LABEL maintainer="cambridgelogic.com"

ENV PYTHONUNBUFFERED=1 
 
WORKDIR /code

COPY requirements.txt /code/
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh

RUN pip install --upgrade pip && \ 
pip install --no-cache-dir -r requirements.txt

ARG NODE_MAJOR=20

RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man && \
    apt-get clean



COPY . /code/

RUN SECRET_KEY=nothing python manage.py tailwind install --no-input && \
    SECRET_KEY=nothing python manage.py tailwind build --no-input && \
    SECRET_KEY=nothing python manage.py collectstatic --no-input

EXPOSE 1091

# Command to run the application
CMD ["gunicorn", "md_app.wsgi:application", "--bind", "0.0.0.0:1091"]

