# Use an official Python runtime as a parent image
FROM python:3.10.6-buster

# Set the working directory
WORKDIR /app


# Copy the current directory contents into the container at /app
COPY . /app

COPY raw_data/Final_df_model_lc_2015_2024.csv /app/raw_data/Final_df_model_lc_2015_2024.csv



# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt


# Make port 80 available to the world outside this container
EXPOSE 80

# Run uvicorn server for FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80"]
