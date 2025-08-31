import cv2

# Apri la webcam (0 = webcam predefinita)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Errore: impossibile aprire la webcam")
    exit()

while True:
    # Leggi un frame dalla webcam
    ret, frame = cap.read()
    if not ret:
        print("Errore: impossibile leggere il frame")
        break

    # Mostra il frame
    cv2.imshow("Frame", frame)

    # Esci se premi 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia la webcam e chiudi le finestre
cap.release()
cv2.destroyAllWindows()
