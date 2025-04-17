# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
