"""
Main application for gesture recognition and robot control using Unitree Go2 SDK.
This script provides two modes of operation:
1. Debug mode: Uses the computer's webcam to capture frames and perform hand gesture recognition.
2. Normal mode: Connects to the Unitree Go2 robot, receives video frames from its camera, and controls the robot based on recognized hand gestures.
Modules and Classes:
--------------------
- Imports Unitree SDK modules for robot communication and video streaming.
- Imports custom HandReader and DogState for gesture recognition and mapping gestures to robot actions.
- Uses OpenCV for image processing and annotation.
- Uses mmap for efficient frame sharing between processes.
Constants:
----------
- FRAME_PATH: Path to the raw frame file for sharing annotated frames.
- FRAMESIZE_FILE_PATH: Path to the file storing frame dimensions.
Functions:
----------
- useComputerCamera():
    # Captures frames from the computer's webcam.
    # Initializes frame size and memory-mapped file for frame sharing.
    # Annotates frames using HandReader and writes them to shared memory.
- useDogCamera(internet_card):
    # Initializes communication with the Unitree Go2 robot using the specified network interface.
    # Subscribes to robot state and battery state channels.
    # Initializes SportMode for gesture-to-action mapping.
    # Receives video frames from the robot, annotates them, overlays battery status, and writes to shared memory.
    # Detects gesture changes and triggers corresponding robot actions in a separate thread.
Classes:
--------
- SportMode:
    # Manages robot actions mapped to hand gestures.
    # Stores initial robot position and yaw.
    # Provides methods to update initial state and trigger robot movements.
Global Variables:
-----------------
- robot_state: Stores the latest robot state received from the robot.
- battery_level: Stores the latest battery level received from the robot.
Handlers:
---------
- HighStateHandler(msg):
    # Updates global robot_state with the latest received message.
- BmsStateHandler(msg):
    # Updates global battery_level with the latest received message.
Main Execution:
---------------
- Checks DEBUG environment variable to select mode.
- In debug mode, uses the computer's webcam.
- In normal mode, connects to the robot and starts gesture recognition and control loop.
Usage:
------
Run the script directly to start gesture recognition and robot control.
Set the DEBUG environment variable to use the computer's webcam for testing.
"""
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
    """
    Captures video frames from the computer's default webcam, processes each frame to detect and annotate hand gestures,
    and writes the annotated frame data to a memory-mapped binary file for inter-process communication.
    Workflow:
        1. Opens the default webcam (device 0) using OpenCV.
        2. Retrieves the frame width and height, and calculates the frame size in bytes (BGR format).
        3. Writes the frame dimensions to a specified file.
        4. Initializes a binary file for frame data and sets up memory mapping for efficient shared access.
        5. Continuously reads frames from the webcam, annotates them using a hand gesture recognition module,
           and writes the annotated frame to the memory-mapped file.
        6. Handles errors if the webcam or frame cannot be accessed.
        7. Releases the webcam resource upon completion.
    Side Effects:
        - Writes frame dimensions and annotated frame data to specified files.
        - Uses memory mapping for efficient frame sharing.
    Dependencies:
        - cv2 (OpenCV)
        - mmap
        - HandReader (hand gesture recognition class)
        - FRAMESIZE_FILE_PATH (path to frame size file)
        - FRAME_PATH (path to frame data file)
    Note:
        This function runs an infinite loop until a frame cannot be read from the webcam.
    """
    cap = cv2.VideoCapture(0)  # Open the default webcam (device 0)

    if not cap.isOpened():  # Check if the webcam is accessible
        print("Errore: impossibile aprire la webcam")
        return

    width, height = int(cap.get(3)), int(cap.get(4))  # Get frame width and height
    frame_size = width * height * 3  # Calculate frame size in bytes (BGR format)

    with open(FRAMESIZE_FILE_PATH, "w") as f:  # Write frame dimensions to file
        f.write(f"{width} {height}")

    with open(FRAME_PATH, "wb") as f:  # Initialize binary file for frame data
        f.write(b'\x00' * frame_size)
    
    with open(FRAME_PATH, "r+b") as f:  # Open frame file for memory mapping
        mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)

        hand_reader = HandReader()  # Initialize hand gesture reader

        while True:  # Main loop to read and process frames
            ret, frame = cap.read()  # Read a frame from the webcam
            if not ret:  # Check if frame was read successfully
                print("Errore: impossibile leggere il frame")
                break

            annotated_frame = hand_reader.Start(frame)  # Annotate frame with hand gestures

            mm.seek(0)  # Move to the start of the memory-mapped file
            mm.write(annotated_frame.tobytes())  # Write annotated frame to shared memory

    cap.release()  # Release the webcam resource


### NORMAL MODE

class SportMode:
    """
    SportMode manages the interaction with a robotic dog using hand gesture recognition.

    Attributes:
        px0 (float): Initial x position of the robot.
        py0 (float): Initial y position of the robot.
        yaw0 (float): Initial yaw (rotation) of the robot.
        client (SportClient): Client interface for controlling the robot in sport mode.
        dog_moves (dict): Mapping of hand gesture states to robot movement methods.

    Methods:
        __init__():
            Initializes the SportMode instance, sets up the sport client, and maps gestures to robot actions.

        GetInitState(robot_state: SportModeState_):
            Sets the initial position and yaw of the robot based on the provided robot state.

        move_dog(move):
            Executes the corresponding robot movement based on the detected hand gesture, unless the gesture is Zero or Empty.
    """
    def __init__(self) -> None:
        # Initial position and yaw
        self.px0 = 0  # Initial x position of the robot
        self.py0 = 0  # Initial y position of the robot
        self.yaw0 = 0  # Initial yaw (rotation) of the robot

        self.client = SportClient()  # Create a sport client for robot control
        self.client.SetTimeout(10.0)  # Set client timeout to 10 seconds
        self.client.Init()  # Initialize the sport client connection

        # Map hand gesture states to corresponding robot movement methods
        self.dog_moves = {
            DogState.HandOpen: self.client.Hello,       # Open hand gesture triggers Hello action
            DogState.HandClose: self.client.FrontPounce, # Closed hand gesture triggers FrontPounce action
            DogState.Vict: self.client.Heart,           # Victory gesture triggers Heart action
            DogState.ThumbU: self.client.StandUp,       # Thumbs up gesture triggers StandUp action
            DogState.ThumbD: self.client.Damp,          # Thumbs down gesture triggers Damp action
            DogState.Point: self.client.Stretch,        # Point gesture triggers Stretch action
        }

    def GetInitState(self, robot_state: SportModeState_):
        # Set initial position and yaw from the robot's state
        self.px0 = robot_state.position[0]  # Set initial x position
        self.py0 = robot_state.position[1]  # Set initial y position
        self.yaw0 = robot_state.imu_state.rpy[2]  # Set initial yaw (rotation)

    def move_dog(self, move):
        # Execute the corresponding robot movement if gesture is not Zero or Empty
        if not move in (DogState.Zero, DogState.Empty):
            self.dog_moves.get(move)()  # Call the mapped movement method


# Initialize the global robot_state variable with a default SportModeState_ object
robot_state = unitree_go_msg_dds__SportModeState_()

# Handler function for receiving and updating the robot's high-level state
def HighStateHandler(msg: SportModeState_):
    global robot_state  # Declare robot_state as global to modify it
    robot_state = msg   # Update the global robot_state with the received message

# Initialize the global battery_level variable with a default value
battery_level = -1

# Handler function for receiving and updating the robot's battery state
def BmsStateHandler(msg: LowState_):
    global battery_level  # Declare battery_level as global to modify it
    battery_state: BmsState_ = msg.bms_state  # Extract the battery state from the message
    battery_level = int(battery_state.soc)    # Update battery_level with the state of charge (soc) as an integer

def useDogCamera(internet_card):
    """
    Initializes and manages the connection to the Unitree robot's camera and state channels, 
    processes live video frames for hand gesture recognition, and controls robot movement based on detected gestures.


    Workflow:
        - Initializes communication with the robot using the specified network card.
        - Subscribes to sport mode and low-level state channels to monitor robot status and battery level.
        - Establishes a video client connection to the robot's camera.
        - Retrieves an initial image sample to determine frame size and sets up shared memory for frame exchange.
        - Continuously captures video frames, processes them for hand gesture recognition, and overlays battery status.
        - Writes annotated frames to shared memory for external access.
        - Detects changes in hand gesture state and triggers robot movement in a separate thread accordingly.

    Raises:
        SystemExit: If unable to connect to the robot or initialize the camera.
        cv2.error: If there is an error in image processing.

    Side Effects:
        - Writes frame size and frame data to files specified by FRAMESIZE_FILE_PATH and FRAME_PATH.
        - Updates global battery_level variable.
        - Prints status and error messages to the console.
        - Starts threads to control robot movement based on hand gesture recognition.
    """
    try:
        ChannelFactoryInitialize(0, internet_card)  # Initialize communication with the robot using the specified network card
    except:
        print(f"Non è stato possibile collegarsi al cane usando la interfaccia di rete fornita ({internet_card})\n errore di digitazione o di configurazione? chi lo sà :)")
        sys.exit(1)  # Exit if unable to connect

    # Connection to sport node
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)  # Subscribe to sport mode state channel
    sub.Init(HighStateHandler, 10)  # Initialize subscription with handler

    # Connection to low level node
    sub_battery = ChannelSubscriber("rt/lowstate", LowState_)  # Subscribe to low-level state channel
    sub_battery.Init(BmsStateHandler, 10)  # Initialize subscription with handler

    time.sleep(1)  # Wait to ensure connections are established

    sport = SportMode()  # Initialize sport mode controller
    sport.GetInitState(robot_state)  # Retrieve initial robot state
    print("Sport mode avviata con successo !!!")  # Print confirmation

    dog_state = DogState.Empty  # Set initial dog state to empty

    try:
        client = VideoClient()  # Initialize video client for robot's camera
        client.SetTimeout(3.0)  # Set timeout for video client
        client.Init()  # Initialize video client connection
    except Exception as e:
        print(f"C'è stato un problema con la telecamera del cane...\nErrore: {e}")
        sys.exit(2)  # Exit if camera initialization fails

    hand_reader = HandReader()  # Initialize hand gesture reader

    # get sample image
    code = -1
    while code != 0:
        code, data = client.GetImageSample()  # Attempt to retrieve a valid image sample
        print("errore immagine")  # Print error if retrieval fails

    # Convert to numpy image
    image_data = np.frombuffer(bytes(data), dtype=np.uint8)  # Convert image data to numpy array
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)  # Decode image as color

    height, width = image.shape[:2]  # Extract image dimensions
    frame_size = width * height * 3  # Calculate frame size in bytes (BGR)

    with open(FRAMESIZE_FILE_PATH, "w") as f:
        f.write(f"{width} {height}")  # Write frame size to file

    with open(FRAME_PATH, "wb") as f:
        f.write(b'\x00' * frame_size)  # Create binary file for frame, initialize with zeros

    with open(FRAME_PATH, "r+b") as f:
        mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_WRITE)  # Open frame file with memory mapping

        t = None  # Thread for robot movement

        global battery_level
        while True:
            # Get Image data from Go2 robot
            code, data = client.GetImageSample()  # Retrieve image data from robot's camera
            if code != 0:
                print("Get image sample error. code:", code)  # Print error if retrieval fails
                continue

            try:
                # Convert to numpy image
                image_data = np.frombuffer(bytes(data), dtype=np.uint8)  # Convert image data to numpy array
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)  # Decode image as color

                frame = cv2.flip(image, 1)  # Flip image horizontally
                annotated_frame = hand_reader.Start(frame)  # Annotate frame using hand gesture reader

                # Determine battery level color coding
                if battery_level < 25:
                    battery_color = (0, 0, 255)  # Red for low battery
                elif battery_level < 60:
                    battery_color = (0, 165, 255)  # Orange for medium battery
                else:
                    battery_color = (0, 255, 0)  # Green for high battery

                # Overlay battery percentage on the frame
                cv2.putText(annotated_frame, str(battery_level) + '%', (width-100, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, battery_color, 2, cv2.LINE_AA)

                # write frame
                mm.seek(0)  # Move to start of memory-mapped file
                mm.write(annotated_frame.tobytes())  # Write annotated frame to shared memory

                # If the detected dog state changes, start a new thread to move the robot accordingly
                if(dog_state != hand_reader.dog_state):
                    dog_state = hand_reader.dog_state

                    if t is None or not t.is_alive():  # Start new thread if previous is not alive
                        t = threading.Thread(target=sport.move_dog, args=(dog_state,))
                        t.daemon = True  # Set thread as daemon
                        t.start()
            except cv2.error as e:
                print(e)  # Handle OpenCV errors gracefully
                continue


if __name__ == "__main__":  # Entry point for the script
    debug = os.getenv("DEBUG", 0)  # Get DEBUG environment variable (default to 0 if not set)
    internet_card = "eth0"  # Set default network interface for robot connection

    if debug:  # If debug mode is enabled
        useComputerCamera()  # Use the computer's webcam for gesture recognition
    else:  # If not in debug mode
        useDogCamera(internet_card)  # Connect to the robot and use its camera for gesture recognition
