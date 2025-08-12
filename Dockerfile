# Defines the container for the FastAPI application.
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install uv, the fast package manager
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency configuration files first
COPY pyproject.toml ./

# Install project dependencies using uv
RUN uv pip install --system --no-cache -e .

# Copy the rest of the application source code
COPY ./app /app/app

# The command to run the application
CMD ["uv", "run", "start"]
