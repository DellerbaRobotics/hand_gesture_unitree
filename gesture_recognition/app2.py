from unitreesdk2.unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitreesdk2.unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitreesdk2.unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_
from unitreesdk2.unitree_sdk2py.go2.sport.sport_client import SportClient
from unitreesdk2.unitree_sdk2py.go2.video.video_client import VideoClient
from numpy import ndarray

import sys, time, cv2, argparse
import mediapipe as mp
import numpy as np
import mmap
import os


class SportMode:
    def __init__(self) -> None:
        # Initial position and yaw
        self.px0 = 0
        self.py0 = 0
        self.yaw0 = 0

        self.client = SportClient()  # Create a sport client
        self.client.SetTimeout(10.0)
        self.client.Init()

    def GetInitState(self, robot_state: SportModeState_):
        self.px0 = robot_state.position[0]
        self.py0 = robot_state.position[1]
        self.yaw0 = robot_state.imu_state.rpy[2]

    def StandUp(self):
        self.client.StandUp()
        print("Stand up !!!")
        #time.sleep(1)

    def StandDown(self):
        self.client.StandDown()
        print("Stand down !!!")
        #time.sleep(1)

# Robot state
robot_state = unitree_go_msg_dds__SportModeState_()
def HighStateHandler(msg: SportModeState_):
    global robot_state
    robot_state = msg

def init_robot(debug: bool, card: str) -> SportMode:
    if not debug:
        try:
            ChannelFactoryInitialize(0, card)
        except:
            print("Non è stato possibile collegarsi al cane usando la interfaccia di rete fornita ({card})\n errore di digitazione o di configurazione? chi lo sà :)".format(card=card))
            exit(0)            
        sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
        sub.Init(HighStateHandler, 10)
        time.sleep(1)

        sport = SportMode()
        sport.GetInitState(robot_state)

        print("Sport mode avviata con successo !!!")
        return sport

def getComputerCamera(debug: bool) -> None:
    if not debug:
        return
    

    # Apri la webcam (0 = webcam predefinita, prova 1 se hai più camere)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore: impossibile aprire la webcam")
        return

    width, height = int(cap.get(3)), int(cap.get(4))
    frame_size = width * height * 3  # BGR
    frame_path = "/stream/frame.raw"

    with open(frame_path, "wb") as f:
        f.write(b'\x00' * frame_size)
    
    with open(frame_path, "r+b") as f:
        mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)

        while True:
            # Leggi un frame dalla webcam
            ret, frame = cap.read()
            if not ret:
                print("Errore: impossibile leggere il frame")
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            process_hand(image_rgb, frame)

            mm.seek(0)
            mm.write(frame.tobytes())


    cap.release()

def getDogCamera(debug: bool) -> None:
    if debug:
        return
    
    try:
        client = VideoClient()
        client.SetTimeout(3.0)
        client.Init()
    except Exception as e:
        print("C'è stato un problema con la telecamera del cane...\nErrore: {e}".format(e=e))
        exit(1)

    code, data = client.GetImageSample()
    print("Camera connessa codice: {}".format(code))
    while code == 0:
        # Get Image data from Go2 robot
        code, data = client.GetImageSample()
        print(code)
        if code != 0:
            break

        # Convert to numpy image
        image_data = np.frombuffer(bytes(data), dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        # Process the image and detect hand gestures
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        process_hand(image_rgb, image)

        # send_frame_udp(image)


def process_hand(image_data: ndarray, image) -> None:
    result = hands.process(image_data)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # thumb finger (pollice)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
            arg = 'down' if thumb_tip.y > thumb_ip.y else 'up'
            
            robot_exec(debug, arg)


def robot_exec(debug: bool, arg: str) -> None: #sport: SportMode, 

    if debug:
        return
    
    cmd_f = [sport.StandUp, sport.StandDown]
    cmd   = ["up", "down"]

    for i in range(len(cmd)):
        if arg.lower() == cmd[i]:
            print("sto esegunedo: {}".format(cmd[i]))
            cmd_f[i]()
            return
    
    print("La funzione richiesta non è stata trovata!")

if __name__ == "__main__":
    
    a = argparse.ArgumentParser(
        prog="Gesture Camera", 
        description="Con questo programma sarà possibile comandare il cane della unitree (go2) con il movimento delle mani", 
        epilog="Creato dall'IISS Luigi dell'erba")
    
    a.add_argument("-internet_card", required=False, default="eth0")
    a.add_argument("-d", "--debug", default=True)

    args = a.parse_args()

    debug = args.debug
    card = args.internet_card
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    getComputerCamera(debug)
    sport = init_robot(debug, card)    
    
    getDogCamera(debug)
