from unitreesdk2.unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitreesdk2.unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitreesdk2.unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitreesdk2.unitree_sdk2py.go2.sport.sport_client import SportClient
from unitreesdk2.unitree_sdk2py.go2.video.video_client import VideoClient
from numpy import ndarray
from prova2 import HandReader, DogState

import sys, time, cv2, argparse
import mediapipe as mp
import numpy as np
import mmap
import os


### CONSTANTS
FRAME_PATH = "/stream/frame.raw"
FRAMESIZE_FILE_PATH = "/stream/framesize.txt"


### DEBUG MODE

def useComputerCamera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore: impossibile aprire la webcam")
        return

    width, height = int(cap.get(3)), int(cap.get(4))
    frame_size = width * height * 3  # BGR

    with open(FRAMESIZE_FILE_PATH, "w") as f:
        f.write(f"{width} {height}")

    with open(FRAME_PATH, "wb") as f:
        f.write(b'\x00' * frame_size)
    
    f = open(FRAME_PATH, "r+b")
    mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)

    hand_reader = HandReader()

    while True:
        # Leggi un frame dalla webcam
        ret, frame = cap.read()
        if not ret:
            print("Errore: impossibile leggere il frame")
            break

        annotated_frame = hand_reader.Start(frame)

        mm.seek(0)
        mm.write(annotated_frame.tobytes())

    cap.release()
    f.close()


### NORMAL MODE

class SportMode:
    def __init__(self) -> None:
        # Initial position and yaw
        self.px0 = 0
        self.py0 = 0
        self.yaw0 = 0

        self.client = SportClient()  # Create a sport client
        self.client.SetTimeout(10.0)
        self.client.Init()

        self.dog_moves = {
            DogState.HandOpen: self.client.Hello(),
            DogState.HandClose: self.client.FrontPounce(),
            DogState.Vict: self.client.Heart(),
            DogState.ThumbU: self.client.StandUp(),
            DogState.ThumbD: self.client.StandDown(),
            DogState.Point: self.client.Stretch(),
        }

    def GetInitState(self, robot_state: SportModeState_):
        self.px0 = robot_state.position[0]
        self.py0 = robot_state.position[1]
        self.yaw0 = robot_state.imu_state.rpy[2]

    def move_dog(self, move):
        self.dog_moves.get(move)()


robot_state = unitree_go_msg_dds__SportModeState_()
def HighStateHandler(msg: SportModeState_):
    global robot_state
    robot_state = msg

def useDogCamera(internet_card):
    try:
        ChannelFactoryInitialize(0, internet_card)
    except:
        print(f"Non è stato possibile collegarsi al cane usando la interfaccia di rete fornita ({internet_card})\n errore di digitazione o di configurazione? chi lo sà :)")
        sys.exit(1)
    
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub.Init(HighStateHandler, 10)
    time.sleep(1)

    sport = SportMode()
    sport.GetInitState(robot_state)
    print("Sport mode avviata con successo !!!")

    dog_state = DogState.Empty

    try:
        client = VideoClient()
        client.SetTimeout(3.0)
        client.Init()
    except Exception as e:
        print(f"C'è stato un problema con la telecamera del cane...\nErrore: {e}")
        sys.exit(2)

    hand_reader = HandReader()

    # get sample image
    code, data = client.GetImageSample()
    # width, height = int(cap.get(3)), int(cap.get(4))
    width, height = 1280, 720
    frame_size = width * height * 3  # BGR

    with open(FRAMESIZE_FILE_PATH, "w") as f:
        print(f"{width=} {height=}")
        f.write(width, height)

    with open(FRAME_PATH, "wb") as f:
        f.write(b'\x00' * frame_size)
    
    f = open(FRAME_PATH, "r+b")
    mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)

    while True:
        # Get Image data from Go2 robot
        code, data = client.GetImageSample()
        if code != 0:
            print("Get image sample error. code:", code)
            break

        # Convert to numpy image
        image_data = np.frombuffer(bytes(data), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        frame = cv2.flip(image, 1)
        annotated_frame = hand_reader.Start(frame)

        # write frame
        mm.seek(0)
        mm.write(annotated_frame.tobytes())

        if(dog_state != hand_reader.dog_state):
            dog_state = hand_reader.dog_state
            sport.move_dog(dog_state)
    
    f.close()



if __name__ == "__main__":
    
    a = argparse.ArgumentParser(
        prog="Gesture Camera", 
        description="Con questo programma sarà possibile comandare il cane della unitree (go2) con il movimento delle mani", 
        epilog="Creato dall'IISS Luigi dell'erba")
    
    a.add_argument("-internet_card", required=False, default="eth0")
    a.add_argument("-d", "--debug", default=False)

    args = a.parse_args()

    debug = args.debug
    internet_card = args.internet_card


    if debug:
        useComputerCamera()
    else:
        useDogCamera(internet_card)
