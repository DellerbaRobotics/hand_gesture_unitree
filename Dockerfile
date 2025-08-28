FROM ubuntu:20.04

RUN apt update && \ apt install -y python3.10 python3.10-venv python3.10-disutils python3.10-pip && \ apt clean && \ rm -rf /var/lib/apt/lists/* 

RUN pip3.10 install -e .
RUN pip3.10 install -r requirements.txt
RUN bash -c $ETH
CMD ["python3.10", "/Users/mirko/Documents/GitHub/hand_gesture_unitree/example/go2/high_level/hand_gesture_front_camera.py", $ETH]