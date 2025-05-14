# Base image
FROM mcr.microsoft.com/devcontainers/python:3.12

# Set the working directory
WORKDIR /workspace

# Copy the project files into the container
COPY . /workspace

# Ensure the requirements.txt file exists before running pip
RUN if [ -f "requirements.txt" ]; then \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt; \
    else echo "requirements.txt not found, skipping pip install"; \
    fi

# Expose the default Flask port
EXPOSE 5000

# Set the default user to root
USER root
