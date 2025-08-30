FROM ubuntu:22.04

# RUN apt update && apt install -y \
#     software-properties-common \
#     curl \
#     lsb-release \
#     gnupg2 
    
# RUN add-apt-repository ppa:deadsnakes/ppa && apt update

RUN apt update && apt install -y python3.10 python3-pip

COPY . /app
WORKDIR /app

RUN apt install -y libglib2.0-0 libsm6 libxrender1 libxext6 ffmpeg libsm6 libxext6 libgl1

RUN pip3.10 install -e ./unitreesdk2/.

RUN pip3.10 install -r requirements.txt

ENTRYPOINT ["python3.10", "./gesture_camera.py"]
