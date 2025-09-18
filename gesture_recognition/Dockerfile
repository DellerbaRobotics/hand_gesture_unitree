# This Dockerfile builds an Ubuntu 22.04-based image for a Python 3.10 hand gesture recognition app.
# It uses build cache for apt and pip to speed up builds, installs dependencies, copies source files,
# installs a local Python package, and sets the entrypoint to run the app.

FROM ubuntu:22.04 

# Cache APT
RUN --mount=type=cache,target=/var/cache/apt \ 
    --mount=type=cache,target=/var/lib/apt/lists \ 
    apt-get update && \ 
    apt-get install -y python3.10 python3-pip libgl1 libglib2.0-0 && \ 
    rm -rf /var/lib/apt/lists/* 

WORKDIR /app 
COPY requirements.txt . 

# COPY app.py .  # (Commented out) Would copy app.py to the container
# COPY hand_reader.py .  # (Commented out) Would copy hand_reader.py to the container
# COPY gesture_recognizer.task .  # (Commented out) Would copy gesture_recognizer.task to the container
COPY unitreesdk2 ./unitreesdk2  

# Cache pip
RUN --mount=type=cache,target=/root/.cache/pip \  
    pip3.10 install -e ./unitreesdk2/.  

RUN --mount=type=cache,target=/root/.cache/pip \  
    pip3.10 install -r requirements.txt  

ENTRYPOINT ["python3.10", "./app.py"]  