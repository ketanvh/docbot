# Base image from the dev container
FROM mcr.microsoft.com/devcontainers/python:3.12

# Set working directory
WORKDIR /home/site/wwwroot

# Copy the project files
COPY . /home/site/wwwroot/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Create session directory
RUN mkdir -p /home/site/wwwroot/flask_session && \
    chmod -R 755 /home/site/wwwroot/flask_session

# Expose the port
EXPOSE 8000

# Set startup command
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--timeout", "600", "app:app"]
