#autore Luigi Loliva
#autore Luca Luisi
#data 16/09/25
#Descrizione: programma che riconosce i gesti di una mana classificandoli in n Tipi


import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import cv2
import enum
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#enum con gli stati del cane
class DogState(enum.Enum):
    Vict = 0
    ThumbU = 1
    ThumbD = 2
    Point = 3
    HandClose = 4
    HandOpen = 5
    Empty = 6
    Zero = 7

#converte l'enum dal testo
def ConvTextToEnum(str):
    if(str == "Victory"):
        return DogState.Vict
    elif(str == "None"):
        return DogState.Zero
    elif(str == "Thumb_Up"):
        return DogState.ThumbU
    elif(str == "Thumb_Down"):
        return DogState.ThumbD
    elif(str == "Open_Palm"):
        return DogState.HandOpen
    elif(str == "Closed_Fist"):
        return DogState.HandClose
    elif(str == "Pointing_Up"):
        return DogState.Point
    
class HandReader():

    def __init__(self):
        self.dog_state = DogState.Empty #imposto lo stato a vuoto
        self.count = 0
        #variabile che memorizza l'ultimo gesto
        self.lastGesture = "ciao"

        # Inizializza MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Inizializza il riconoscitore
        self.base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        self.options = vision.GestureRecognizerOptions(base_options=self.base_options)
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)
    
    # Funzione per elaborare una singola immagine (frame) con gesture e landmarks
    def display_single_image_with_gesture_and_hand_landmarks(self, image_bgr, result):
        gesture, hand_landmarks_list = result
        annotated_image = image_bgr.copy()
        for hand_landmarks in hand_landmarks_list:
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            self.mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )


        # Sovrascrivi il testo del gesto riconosciuto
        title = f"{gesture.category_name} ({gesture.score:.2f})"
        cv2.putText(annotated_image, title, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        
        #controllo se il gesto supera il livello di confidenza e se è diverso dall'ultimo
        #primo gesto valido
        if(gesture.score > 0.50 and self.dog_state == DogState.Empty):
            self.lastGesture = gesture.category_name

            self.dog_state = ConvTextToEnum(gesture.category_name)

            print(gesture.category_name)

            self.count = 0
        elif(gesture.score > 0.50 and self.dog_state != ConvTextToEnum(gesture.category_name)):
            #cambio di gesto
            self.lastGesture = gesture.category_name

            self.dog_state = ConvTextToEnum(gesture.category_name)

        elif(self.dog_state == ConvTextToEnum(gesture.category_name)):
            #non ce stato un cambiamento di gesto
            ...
        elif ConvTextToEnum(gesture.category_name) == DogState.Zero and self.dog_state != DogState.Zero:
            self.dog_state = DogState.Zero
        # elif(self.count == 0):
        #     print(f"non ci sono variazioni l'ultimo gesto è {self.lastGesture}")
        #     self.count += 1
        return annotated_image
    
    def Start(self, frame):
        # Converti da BGR a RGB per MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Esegui il riconoscimento
        recognition_result = self.recognizer.recognize(mp_image)
        if recognition_result.gestures:
            top_gesture = recognition_result.gestures[0][0]
            hand_landmarks = recognition_result.hand_landmarks
            annotated_frame = self.display_single_image_with_gesture_and_hand_landmarks(frame, (top_gesture, hand_landmarks))
        else:
            annotated_frame = frame.copy()
            cv2.putText(annotated_frame, "Nessun gesto rilevato", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            if(self.dog_state != DogState.Empty):
                self.lastGesture = "empty"
                self.dog_state = DogState.Empty
                print("nessun gesto")
        return annotated_frame

def main():
    hR = HandReader() #crea l'oggetto hR
    # Avvia webcam
    cam = cv2.VideoCapture(0)
    print("Premi 'q' per uscire.")
    while True:
        ret, frame = cam.read() #legge il frame
        if not ret:
            print("Errore nella lettura della videocamera.")
            break
        frame = cv2.flip(frame, 1)
        annotated_frame = hR.Start(frame) #inizio analisi del frame
        # Mostra l'immagine
        cv2.imshow('Gesture Recognition', annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # Pulisci
    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main() 
