# Base image
FROM python:latest


RUN mkdir /src
RUN mkdir /src/fuel_service
RUN touch /src/__init__.py

# Copy the necessary files to the container
COPY requirements.txt .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src/fuel_service

# Expose the port for FastAPI
EXPOSE 8001

# Run the FastAPI application
CMD ["uvicorn", "src.fuel_service.main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]
