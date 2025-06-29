# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, the package installer
RUN pip install uv

# Copy the project files and install dependencies
# This leverages Docker's layer caching
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache -r requirements.lock

# Copy the rest of the application's code into the container at /app
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run the app
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
