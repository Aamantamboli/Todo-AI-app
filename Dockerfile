# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker cache if unchanged
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app code into container
COPY . .

# Expose the port your app runs on (adjust if needed)
EXPOSE 5000

# Command to run your app
CMD ["python3", "app.py"]
