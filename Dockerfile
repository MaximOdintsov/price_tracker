## Dockerfile

# Base image with Python
FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-openbsd

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy project code
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Collect static files for Nginx
RUN python manage.py collectstatic

EXPOSE 8000

# Run Daphne ASGI server for Django Channels
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "crypto_project.routing:application"]
