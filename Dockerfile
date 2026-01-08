FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

# Create a writable directory for non-root user (Hugging Face specific)
RUN mkdir -p /code/.cache && chmod -R 777 /code

# Hugging Face Spaces runs on port 7860 by default
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
