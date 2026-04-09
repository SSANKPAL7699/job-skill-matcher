# Start from an official Python image.
# "slim" means it's a lightweight version — smaller file size,
# faster to download and run. We use 3.11 to match our dev environment.
FROM python:3.11-slim

# Set the working directory INSIDE the container.
# Think of it like cd-ing into a folder inside Docker's mini computer.
# All commands after this run from /app
WORKDIR /app

# Copy requirements.txt into the container FIRST.
# Why first? Because Docker caches each step.
# If requirements.txt hasn't changed, Docker skips the pip install step
# and uses the cached version — makes rebuilding much faster.
COPY requirements.txt .

# Install all our Python libraries inside the container.
# --no-cache-dir means don't save the download cache,
# keeps our container image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# NOW copy all our project files into the container.
# We do this AFTER pip install so code changes don't
# invalidate the pip install cache layer.
COPY . .

# Tell Docker our app listens on port 8000.
# This doesn't actually open the port — docker-compose does that.
# It's just documentation for other developers.
EXPOSE 8000

# The command that runs when the container starts.
# uvicorn = the server
# app.main:app = look in app/main.py for the variable called "app"
# --host 0.0.0.0 = accept connections from outside the container
# --port 8000 = listen on port 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}