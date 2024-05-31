# Use an official Python runtime as a parent image
FROM python:3.10.6-buster

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN pip install .
# Run uvicorn server for FastAPI
RUN uvicorn api.main:app --host 0.0.0.0 --port $PORT
