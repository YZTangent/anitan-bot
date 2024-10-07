FROM python:3.12-slim

# Set environment variables (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# Install system dependencies required for your application
RUN apt-get update && apt-get install -y \
  gcc \
  libffi-dev \
  && rm -rf /var/lib/apt/lists/*

# Set up the working directory and install dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock /app/
RUN pip install poetry && poetry install --no-dev

COPY . /app/

# Run the application
CMD ["poetry", "run", "python", "anitan_bot/main.py"]

