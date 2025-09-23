import time  # Import time module for sleep and timing
import sys  # Import sys module for command-line arguments
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize  # Import channel classes for robot communication
from unitree_sdk2py.idl.default import unitree_go_msg_dds__SportModeState_  # Import default robot state message
from unitree_sdk2py.idl.unitree_go.msg.dds_ import SportModeState_  # Import robot sport mode state message
from unitree_sdk2py.go2.sport.sport_client import SportClient  # Import sport client for robot control
from unitree_sdk2py.go2.video.video_client import VideoClient  # Import video client for camera access
import cv2  # Import OpenCV for image processing
import numpy as np  # Import NumPy for array manipulation
import mediapipe as mp  # Import MediaPipe for hand gesture recognition

class SportModeTest:
    """
    SportModeTest provides an interface to control and test the sport mode functionalities of a robot using the SportClient.
    Attributes:
        px0 (float): Initial x position of the robot.
        py0 (float): Initial y position of the robot.
        yaw0 (float): Initial yaw angle of the robot.
        client (SportClient): Instance of the sport client used to communicate with the robot.
    Methods:
        __init__():
            Initializes the SportModeTest instance, sets up the sport client, and configures timeout.
        GetInitState(robot_state: SportModeState_):
            Updates the initial position and yaw attributes using the provided robot state.
        StandUp():
            Commands the robot to stand up and prints a status message.
        StandDown():
            Commands the robot to stand down and prints a status message.
    """
    def __init__(self) -> None:
        """
        Initializes the object with default position and yaw values, and sets up the SportClient.
        - Sets initial x (`self.px0`), y (`self.py0`), and yaw (`self.yaw0`) to 0.
        - Creates a `SportClient` instance (`self.client`).
        - Configures the client with a 10-second timeout.
        - Initializes the client for further operations.
        """
        # Initial position and yaw
        self.px0 = 0  # Initial x position
        self.py0 = 0  # Initial y position
        self.yaw0 = 0  # Initial yaw angle

        self.client = SportClient()  # Create a sport client
        self.client.SetTimeout(10.0)  # Set timeout for client operations
        self.client.Init()  # Initialize the sport client

    def GetInitState(self, robot_state: SportModeState_):
        """
        Initializes the robot's initial state by storing its starting position and yaw angle.

        Args:
            robot_state (SportModeState_): The current state of the robot, containing position and IMU data.

        Attributes Set:
            self.px0 (float): Initial x position of the robot.
            self.py0 (float): Initial y position of the robot.
            self.yaw0 (float): Initial yaw angle (rotation around the z-axis) from the robot's IMU state.
        """
        self.px0 = robot_state.position[0]  # Get initial x position from robot state
        self.py0 = robot_state.position[1]  # Get initial y position from robot state
        self.yaw0 = robot_state.imu_state.rpy[2]  # Get initial yaw from robot IMU state

    def StandUp(self):
        """
        Commands the robot to stand up.

        This method sends a stand-up command to the robot via the client interface
        and prints a status message to indicate the action. Optionally, a sleep
        period can be added after the command to allow the robot time to complete
        the action.

        Returns:
            None
        """
        self.client.StandUp()  # Command robot to stand up
        print("Stand up !!!")  # Print status message
        #time.sleep(1)  # Optional sleep

    def StandDown(self):
        """
        Commands the robot to enter the 'stand down' posture.

        This method sends a 'stand down' command to the robot via the client interface,
        indicating that the robot should lower itself or deactivate its standing position.
        A status message is printed to confirm the action.

        Returns:
            None
        """
        self.client.StandDown()  # Command robot to stand down
        print("Stand down !!!")  # Print status message
        #time.sleep(1)  # Optional sleep

# Robot state
robot_state = unitree_go_msg_dds__SportModeState_()  # Initialize robot state object

def HighStateHandler(msg: SportModeState_):
    """
    Handles updates to the robot's high-level state by assigning the received SportModeState_ message to the global robot_state variable.

    Args:
        msg (SportModeState_): The message containing the latest high-level state information for the robot.

    Side Effects:
        Updates the global variable `robot_state` with the new state information.
    """
    global robot_state
    robot_state = msg  # Update global robot state with new message

if __name__ == "__main__":  # Main entry point
    if len(sys.argv) > 1:  # Check for command-line arguments
        ChannelFactoryInitialize(0, sys.argv[1])  # Initialize channel with argument
    else:
        ChannelFactoryInitialize(0)  # Initialize channel without argument
        
    sub = ChannelSubscriber("rt/sportmodestate", SportModeState_)  # Subscribe to robot state channel
    sub.Init(HighStateHandler, 10)  # Initialize subscriber with handler and queue size
    time.sleep(1)  # Wait for state update

    test = SportModeTest()  # Create sport mode test object
    test.GetInitState(robot_state)  # Set initial state from robot

    print("Start test !!!")  # Print start message

    client = VideoClient()  # Create a video client
    client.SetTimeout(3.0)  # Set timeout for video client
    client.Init()  # Initialize video client

    mp_hands = mp.solutions.hands  # Get MediaPipe hands solution
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)  # Initialize hand detector
    mp_drawing = mp.solutions.drawing_utils  # Get drawing utilities

    code, data = client.GetImageSample()  # Get initial image sample from robot

    while code == 0:  # Loop while image sample is valid
        # Get Image data from Go2 robot
        code, data = client.GetImageSample()  # Get image sample
        if code != 0:  # Check for error
            break  # Exit loop on error

        # Convert to numpy image
        image_data = np.frombuffer(bytes(data), dtype=np.uint8)  # Convert raw data to numpy array
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)  # Decode image from array

        # Process the image and detect hand gestures
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert image to RGB
        result = hands.process(image_rgb)  # Process image for hand landmarks

        if result.multi_hand_landmarks:  # If hand landmarks detected
            for hand_landmarks in result.multi_hand_landmarks:  # Iterate over detected hands
                # Draw hand landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)  # Draw landmarks on image

                # Thumb state detection
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]  # Get thumb tip landmark
                thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]  # Get thumb IP landmark
                thumb_state = 'down' if thumb_tip.y > thumb_ip.y else 'up'  # Determine thumb state

                if thumb_state == 'up':  # If thumb is up
                    test.StandUp()  # Command robot to stand up
                elif thumb_state == 'down':  # If thumb is down
                    test.StandDown()  # Command robot to stand down

        # Display image
        cv2.imshow("front_camera", image)  # Show image in window
        # Press ESC to stop
        if cv2.waitKey(20) == 27:  # Wait for ESC key
            break  # Exit loop

    if code != 0:  # If error occurred
        print("Get image sample error. code:", code)  # Print error code
    else:
        # Capture an image
        cv2.imwrite("front_image.jpg", image)  # Save last image to file

    cv2.destroyWindow("front_camera")  # Close image window
    hands.close()  # Release MediaPipe resources