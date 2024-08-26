FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
