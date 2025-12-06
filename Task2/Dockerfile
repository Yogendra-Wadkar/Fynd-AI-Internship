# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy your files into the container
COPY . /app

# Install the libraries
RUN pip install --no-cache-dir -r requirements.txt

# Tell the container to listen on port 7860 (Hugging Face's default)
EXPOSE 7860

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]