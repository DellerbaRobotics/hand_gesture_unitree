FROM ubuntu:22.04

# Cache APT
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y python3.10 python3-pip libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
# COPY app.py .
# COPY hand_reader.py .
# COPY gesture_recognizer.task .
COPY unitreesdk2 ./unitreesdk2

# Cache pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3.10 install -e ./unitreesdk2/.

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3.10 install -r requirements.txt


ENTRYPOINT ["python3.10", "./app.py"]