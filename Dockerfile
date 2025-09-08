FROM ubuntu:22.04


# Cache APT
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt/lists \
    apt-get update && \
    apt-get install -y python3.10 python3-pip libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg libgl1 && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

# Cache pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3.10 install -e ./unitreesdk2/.

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3.10 install -r requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3.10 install flask


ENTRYPOINT ["python3.10", "./client_server/server.py"]
