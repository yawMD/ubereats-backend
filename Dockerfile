# Use an official Python runtime as a base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
# Install system dependencies including netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*


# Set the working directory in the container
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /code/
COPY . /code/

# Make the entrypoint script executable
COPY entrypoint.sh /code/
RUN chmod +x /code/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the application server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "restaurant.wsgi:application"]
