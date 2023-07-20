# Use the official Python base image
FROM python:latest

RUN mkdir /src
RUN mkdir /src/online_vs_inperson_comparison_service
RUN touch /src/__init__.py

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . /src/online_vs_inperson_comparison_service

# Expose the port that the FastAPI application will run on
EXPOSE 8000

# Start the FastAPI application using uvicorn
CMD ["uvicorn", "src.online_vs_inperson_comparison_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
