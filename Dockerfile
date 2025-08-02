# Base image with Python
FROM python:3.12-slim

# Set environment variables
ENV APP_PATH="/opt/badge-tracker-bot"

# Set working directory inside the container
WORKDIR $APP_PATH

# Install system dependencies
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
  curl nano build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . $APP_PATH

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set the CMD to run the application
CMD ["python3", "bot.py"]
