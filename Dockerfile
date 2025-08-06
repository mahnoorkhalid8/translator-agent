# Base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port
EXPOSE 7860

# Command to run Chainlit
CMD ["chainlit", "run", "main.py", "-h", "0.0.0.0", "-p", "7860"]
