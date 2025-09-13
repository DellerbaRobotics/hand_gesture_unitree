from unitreesdk2.unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitreesdk2.unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_
from unitreesdk2.unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_, LowState_, BmsState_
from unitreesdk2.unitree_sdk2py.go2.sport.sport_client import SportClient
from unitreesdk2.unitree_sdk2py.go2.video.video_client import VideoClient
from hand_reader import HandReader, DogState

import sys, os, time, cv2
import numpy as np
import mmap
import threading


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
    
    with open(FRAME_PATH, "r+b") as f:
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
            DogState.HandOpen: self.client.Hello,
            DogState.HandClose: self.client.FrontPounce,
            DogState.Vict: self.client.Heart,
            DogState.ThumbU: self.client.StandUp,
            DogState.ThumbD: self.client.Damp,
            DogState.Point: self.client.Stretch,
        }

    def GetInitState(self, robot_state: SportModeState_):
        self.px0 = robot_state.position[0]
        self.py0 = robot_state.position[1]
        self.yaw0 = robot_state.imu_state.rpy[2]

    def move_dog(self, move):
        if not move in (DogState.Zero, DogState.Empty):
            self.dog_moves.get(move)()


robot_state = unitree_go_msg_dds__SportModeState_()
def HighStateHandler(msg: SportModeState_):
    global robot_state
    robot_state = msg

battery_level = -1
def BmsStateHandler(msg: LowState_):
    global battery_level
    battery_state: BmsState_ = msg.bms_state
    battery_level = int(battery_state.soc)   

def useDogCamera(internet_card):
    try:
        ChannelFactoryInitialize(0, internet_card)
    except:
        print(f"Non è stato possibile collegarsi al cane usando la interfaccia di rete fornita ({internet_card})\n errore di digitazione o di configurazione? chi lo sà :)")
        sys.exit(1)
    
    # Connection to sport node
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)
    sub.Init(HighStateHandler, 10)

    # Connection to low level node
    sub_battery = ChannelSubscriber("rt/lowstate", LowState_)
    sub_battery.Init(BmsStateHandler, 10)

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
    code = -1
    while code != 0:
        code, data = client.GetImageSample()
        print("errore immagine")
   

    # Convert to numpy image
    image_data = np.frombuffer(bytes(data), dtype=np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    height, width = image.shape[:2]
    frame_size = width * height * 3  # BGR

    with open(FRAMESIZE_FILE_PATH, "w") as f:
        f.write(f"{width} {height}")

    with open(FRAME_PATH, "wb") as f:
        f.write(b'\x00' * frame_size)
    
    with open(FRAME_PATH, "r+b") as f:
        mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)

        t = None

        global battery_level
        while True:
            # Get Image data from Go2 robot
            code, data = client.GetImageSample()
            if code != 0:
                print("Get image sample error. code:", code)
                continue

            try:
                # Convert to numpy image
                image_data = np.frombuffer(bytes(data), dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                frame = cv2.flip(image, 1)
                annotated_frame = hand_reader.Start(frame)

                if battery_level < 25:
                    battery_color = (0, 0, 255)
                elif battery_level < 60:
                    battery_color = (0, 165, 255)
                else:
                    battery_color = (0, 255, 0)

                cv2.putText(annotated_frame, str(battery_level) + '%', (width-100, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, battery_color, 2, cv2.LINE_AA)

                # write frame
                mm.seek(0)
                mm.write(annotated_frame.tobytes())

                if(dog_state != hand_reader.dog_state):
                    dog_state = hand_reader.dog_state
                    
                    if t is None or not t.is_alive():
                        t = threading.Thread(target=sport.move_dog, args=(dog_state,))
                        t.daemon = True
                        t.start()
            except cv2.error as e:
                print(e)
                continue



if __name__ == "__main__":
    debug = os.getenv("DEBUG", 0)
    internet_card = "eth0"

    if debug:
        useComputerCamera()
    else:
        useDogCamera(internet_card)
