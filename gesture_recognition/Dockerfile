# This Dockerfile builds an Ubuntu 22.04-based image for a Python 3.10 hand gesture recognition app.
# It uses build cache for apt and pip to speed up builds, installs dependencies, copies source files,
# installs a local Python package, and sets the entrypoint to run the app.

FROM ubuntu:22.04  # Use Ubuntu 22.04 as the base image

# Cache APT
RUN --mount=type=cache,target=/var/cache/apt \  # Cache /var/cache/apt to speed up apt operations
    --mount=type=cache,target=/var/lib/apt/lists \  # Cache apt package lists
    apt-get update && \  # Update package lists
    apt-get install -y python3.10 python3-pip libgl1 libglib2.0-0 && \  # Install Python 3.10, pip, and required libraries
    rm -rf /var/lib/apt/lists/*  # Clean up apt lists to reduce image size

WORKDIR /app  # Set working directory to /app
COPY requirements.txt .  # Copy requirements.txt to the container

# COPY app.py .  # (Commented out) Would copy app.py to the container
# COPY hand_reader.py .  # (Commented out) Would copy hand_reader.py to the container
# COPY gesture_recognizer.task .  # (Commented out) Would copy gesture_recognizer.task to the container
COPY unitreesdk2 ./unitreesdk2  # Copy the unitreesdk2 directory to the container

# Cache pip
RUN --mount=type=cache,target=/root/.cache/pip \  # Cache pip downloads
    pip3.10 install -e ./unitreesdk2/.  # Install unitreesdk2 as an editable package

RUN --mount=type=cache,target=/root/.cache/pip \  # Cache pip downloads
    pip3.10 install -r requirements.txt  # Install Python dependencies from requirements.txt

ENTRYPOINT ["python3.10", "./app.py"]  # Run app.py with Python 3.10 when the container starts