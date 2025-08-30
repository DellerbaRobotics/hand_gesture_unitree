# Hand Gesture Control for Unitree Robots
Python interface for hand gesture control of unitree_go2_robot. In this project we used OpenCV and Mediapipe.

# Demo
From third person standpoint  

https://github.com/user-attachments/assets/54a42c59-c0c0-4a55-8ecb-3b49060b8116

From robot standpoint


https://github.com/user-attachments/assets/bb01ecc9-5808-4beb-b1c6-61ed2f0799c1



# Installation
## Dependencies
- Python >= 3.8
- cyclonedds == 0.10.2
- numpy
- opencv-python
## Install unitree_sdk2_python

```bash
pip install unitree_sdk2py
```

### Installing from source
Execute the following commands in the terminal:
```bash
cd ~
sudo apt install python3-pip
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python
pip3 install -e .
```
## FAQ
##### 1. Error when `pip3 install -e .`:
```bash
Could not locate cyclonedds. Try to set CYCLONEDDS_HOME or CMAKE_PREFIX_PATH
```
This error mentions that the cyclonedds path could not be found. First compile and install cyclonedds:

```bash
cd ~
git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x 
cd cyclonedds && mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
cmake --build . --target install
```
Enter the unitree_sdk2_python directory, set `CYCLONEDDS_HOME` to the path of the cyclonedds you just compiled, and then install unitree_sdk2_python.
```bash
cd ~/unitree_sdk2_python
export CYCLONEDDS_HOME="~/cyclonedds/install"
pip3 install -e .
```
For details, see: https://pypi.org/project/cyclonedds/#installing-with-pre-built-binaries

# Usage
The Python sdk2 interface maintains consistency with the unitree_sdk2 interface, achieving robot status acquisition and control through request-response or topic subscription/publishing. Example programs are located in the `/example` directory. Before running the examples, configure the robot's network connection as per the instructions in the document at https://support.unitree.com/home/en/developer/Quick_start.
## DDS Communication
In the terminal, execute:
```bash
python3 ./example/helloworld/publisher.py
```
Open a new terminal and execute:
```bash
python3 ./example/helloworld/subscriber.py
```
You will see the data output in the terminal. The data structure transmitted between `publisher.py` and `subscriber.py` is defined in `user_data.py`, and users can define the required data structure as needed.
## High-Level Status and Control
The high-level interface maintains consistency with unitree_sdk2 in terms of data structure and control methods. For detailed information, refer to https://support.unitree.com/home/en/developer/sports_services.
### Run Hand Gesture Control 
Execute the following command in the terminal:
```bash
python3 ./example/high_level/hand_gesture_front_camera.py enp2s0
```
Replace `enp2s0` with the name of the network interface to which the robot is connected,.
