#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

import mediapipe as mp  # Import MediaPipe library for hand recognition
from mediapipe.framework.formats import landmark_pb2  # Import hand landmark format
from mediapipe.tasks import python  # Import MediaPipe tasks for Python
from mediapipe.tasks.python import vision  # Import MediaPipe vision tasks
import enum  # Import enum module for creating enumerations

# Enum with dog states (recognized gestures)
class DogState(enum.Enum):
    Vict = 0        # Victory gesture
    ThumbU = 1      # Thumbs up
    ThumbD = 2      # Thumbs down
    Point = 3       # Pointing up
    HandClose = 4   # Closed hand
    HandOpen = 5    # Open hand
    Empty = 6       # No gesture
    Zero = 7        # Zero/none state

# Converts a string to a DogState enum value
def ConvTextToEnum(str):
    # Check if the gesture is "Victory"
    if(str == "Victory"):
        return DogState.Vict
    # Check if the gesture is "None"
    elif(str == "None"):
        return DogState.Zero
    # Check if the gesture is "Thumb_Up"
    elif(str == "Thumb_Up"):
        return DogState.ThumbU
    # Check if the gesture is "Thumb_Down"
    elif(str == "Thumb_Down"):
        return DogState.ThumbD
    # Check if the gesture is "Open_Palm"
    elif(str == "Open_Palm"):
        return DogState.HandOpen
    # Check if the gesture is "Closed_Fist"
    elif(str == "Closed_Fist"):
        return DogState.HandClose
    # Check if the gesture is "Pointing_Up"
    elif(str == "Pointing_Up"):
        return DogState.Point

# Main class for hand reading and recognition
class HandReader():
    """
    HandReader is a gesture recognition class that uses MediaPipe and a gesture recognition model
    to detect hand gestures from images or video frames. It manages the state of recognized gestures,
    annotates images with gesture information and hand landmarks, and tracks gesture changes.
    Attributes:
        dog_state (DogState): Current state of the recognized gesture.
        count (int): Counter for gesture changes.
        lastGesture (str): Name of the last recognized gesture.
        mp_hands: MediaPipe Hands solution module.
        mp_drawing: MediaPipe drawing utilities.
        mp_drawing_styles: MediaPipe drawing styles.
        base_options: Base options for the gesture recognizer.
        options: Gesture recognizer options.
        recognizer: Gesture recognizer instance.
    Methods:
        __init__():
            Initializes the HandReader, MediaPipe Hands, and gesture recognizer.
        display_single_image_with_gesture_and_hand_landmarks(image_bgr, result):
            Processes a single image, draws detected hand landmarks and connections,
            annotates the image with the recognized gesture name and confidence,
            and updates gesture state logic.
            Args:
                image_bgr (np.ndarray): Input image in BGR format.
                result (tuple): Tuple containing the top gesture and list of hand landmarks.
            Returns:
                np.ndarray: Annotated image with gesture and hand landmarks.
        Start(frame):
            Starts gesture recognition on the given frame, annotates the frame with gesture
            information or a message if no gesture is detected, and updates gesture state.
            Args:
                frame (np.ndarray): Input video frame in BGR format.
            Returns:
                np.ndarray: Annotated frame with gesture information.
    """

    def __init__(self):
        """
        Initializes the HandReader class.

        Sets up the initial state for gesture recognition, including:
        - Setting the dog's state to empty.
        - Initializing a counter for gesture changes.
        - Storing the last recognized gesture.
        - Initializing MediaPipe Hands and drawing utilities.
        - Loading and configuring the gesture recognizer model.

        Attributes:
            dog_state (DogState): The current state of the dog, initially set to empty.
            count (int): Counter for the number of gesture changes detected.
            lastGesture (str): The last recognized gesture.
            mp_hands: MediaPipe Hands solution for hand tracking.
            mp_drawing: MediaPipe drawing utility for rendering hand landmarks.
            mp_drawing_styles: MediaPipe drawing styles for hand landmarks.
            base_options: Base options for the gesture recognizer model.
            options: Gesture recognizer configuration options.
            recognizer: Gesture recognizer instance for detecting hand gestures.
        """
        self.dog_state = DogState.Empty # Set initial state to empty
        self.count = 0  # Counter for gesture changes
        self.lastGesture = "ciao"  # Stores the last recognized gesture

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Initialize gesture recognizer
        self.base_options = python.BaseOptions(model_asset_path='/home/luigi/catkin2_ws/src/gesture_ros/scripts/gesture_recognizer.task') #forzato
        self.options = vision.GestureRecognizerOptions(base_options=self.base_options)
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)
    
    # Processes a single image, draws gesture and landmarks
    def display_single_image_with_gesture_and_hand_landmarks(self, image_bgr, result):
        """
        Annotates a single BGR image with detected hand landmarks and recognized gesture information.
        Args:
            image_bgr (np.ndarray): The input image in BGR format to be annotated.
            result (Tuple[Gesture, List[List[Landmark]]]): A tuple containing the recognized gesture and a list of hand landmarks.
                - gesture: An object with 'category_name' (str) and 'score' (float) attributes representing the gesture name and confidence.
                - hand_landmarks_list: A list of lists, where each inner list contains landmark objects (with x, y, z attributes) for a detected hand.
        Returns:
            np.ndarray: The annotated image with hand landmarks, connections, and gesture information drawn.
        Side Effects:
            - Updates internal state variables (`lastGesture`, `dog_state`, `count`) based on gesture recognition logic.
            - Prints the recognized gesture name to the console when a new valid gesture is detected.
        Notes:
            - Draws hand landmarks and connections using MediaPipe drawing utilities.
            - Displays the gesture name and confidence score on the image.
            - Handles gesture state transitions for further application logic.
        """
        gesture, hand_landmarks_list = result  # Extract gesture and landmarks
        annotated_image = image_bgr.copy()  # Copy image for annotation
        for hand_landmarks in hand_landmarks_list:  # For each detected hand
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()  # Create normalized landmark list
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            # Draw landmarks and connections on the hand
            self.mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )

        # Write recognized gesture name and confidence on the image
        title = f"{gesture.category_name} ({gesture.score:.2f})"
        cv2.putText(annotated_image, title, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        
        # Logic to handle gesture change and state
        if(gesture.score > 0.50 and self.dog_state == DogState.Empty):  # First valid gesture
            self.lastGesture = gesture.category_name
            self.dog_state = ConvTextToEnum(gesture.category_name)
            print(gesture.category_name)
            self.count = 0
        elif(gesture.score > 0.50 and self.dog_state != ConvTextToEnum(gesture.category_name)):  # Gesture change
            self.lastGesture = gesture.category_name
            self.dog_state = ConvTextToEnum(gesture.category_name)
        elif(self.dog_state == ConvTextToEnum(gesture.category_name)):  # No gesture change
            ...
        elif ConvTextToEnum(gesture.category_name) == DogState.Zero and self.dog_state != DogState.Zero:  # "None" gesture
            self.dog_state = DogState.Zero
        return annotated_image  # Return annotated image
    
    # Starts recognition on the given frame
    def Start(self, frame):
        """
        Processes a video frame to detect and recognize hand gestures using MediaPipe.

        Args:
            frame (numpy.ndarray): The input video frame in BGR format.

        Returns:
            numpy.ndarray: The annotated frame with gesture and hand landmarks if detected,
                           or with a "No gesture detected" message otherwise.

        Workflow:
            - Converts the input frame from BGR to RGB.
            - Creates a MediaPipe image object from the RGB frame.
            - Performs gesture recognition on the image.
            - If a gesture is detected:
                - Retrieves the gesture with the highest confidence and hand landmarks.
                - Annotates the frame with gesture and hand landmarks.
            - If no gesture is detected:
                - Annotates the frame with a "No gesture detected" message.
                - Updates internal state variables (`lastGesture` and `dog_state`) if necessary.
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert from BGR to RGB
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)  # Create MediaPipe image object

        recognition_result = self.recognizer.recognize(mp_image)  # Perform recognition
        if recognition_result.gestures:  # If gestures are recognized
            top_gesture = recognition_result.gestures[0][0]  # Get gesture with highest confidence
            hand_landmarks = recognition_result.hand_landmarks  # Get hand landmarks
            annotated_frame = self.display_single_image_with_gesture_and_hand_landmarks(frame, (top_gesture, hand_landmarks))
        else:  # No gesture detected
            annotated_frame = frame.copy()
            cv2.putText(annotated_frame, "No gesture detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if(self.dog_state != DogState.Empty):
                self.lastGesture = "empty"
                self.dog_state = DogState.Empty
                print("no gesture")
        return annotated_frame  # Return annotated frame


def ros_node():
    rospy.init_node('hand_gesture_recognition_node')

    # Publishers
    gesture_pub = rospy.Publisher('recognized_gesture', String, queue_size=10)
    image_pub = rospy.Publisher('gesture_image', Image, queue_size=10)
    
    bridge = CvBridge()
    rate = rospy.Rate(10)  # 10 Hz

    hR = HandReader()
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        rospy.logerr("Camera not opened")
        return
    
    rospy.loginfo("Hand Gesture Recognition Node")
    
    while not rospy.is_shutdown():
        ret, frame = cam.read()
        if not ret:
            rospy.logwarn("Lettura webcam fallita")
            continue

        frame = cv2.flip(frame, 1)
        annotated_frame = hR.Start(frame)

        # Publish annotated image
        try:
            ros_image = bridge.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
            image_pub.publish(ros_image)
        except Exception as e:
            rospy.logwarn(f"cv_bridge exception: {e}")

        # Publish recognized gesture as string
        gesture_str = hR.dog_state.name if hR.dog_state else "Empty"
        gesture_pub.publish(String(data=gesture_str))

        rate.sleep()

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        ros_node()
    except rospy.ROSInterruptException:
        pass