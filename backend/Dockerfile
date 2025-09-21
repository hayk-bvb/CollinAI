# Use an official base image
FROM python:3.12.5


# Set working directory to project root
WORKDIR /

# Set PYTHONPATH to project root
ENV PYTHONPATH="/"

# Install dependencies first for better layer caching
COPY backend/requirements.txt ./requirements.txt
# Copy backend folder and requirements.txt into the container
COPY backend /backend

RUN pip install --no-cache-dir -r backend/requirements.txt


# Run your app
CMD ["python3", "-m", "backend.main"]