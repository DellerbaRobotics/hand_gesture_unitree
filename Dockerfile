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


RUN pip3.10 install -e .

RUN pip3.10 install -r requirements.txt

CMD ["python3.10", "./example/go2/high_level/hand_gesture_front_camera.py"]