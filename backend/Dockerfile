# Use an official base image
FROM python:3.12.5

# Set working directory inside the container
WORKDIR /collinai

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your app
CMD ["python", "main.py"]