FROM python:3.9-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir flask requests

# Copy the mock server code
COPY app.py .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]
