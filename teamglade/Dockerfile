# Pull base image
FROM python:3.10-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy project
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

