import socket
import cv2
import numpy as np

print("Ciao")
IP = "127.0.0.10"
PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen("Sto aspettando la connessione dal cane: {}:{}".format(IP, PORT))

conn, addr = s.accept()

# Prima ricevi la lunghezza dell'immagine (es. 4 byte per la dimensione)
def recvall(sock, count):
    """ Riceve esattamente 'count' bytes dal socket """
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

# Ricevi prima la dimensione dell'immagine (in 4 byte)
lengthbuf = recvall(conn, 4)
length = int.from_bytes(lengthbuf, byteorder='big')

# Ricevi l'immagine vera e propria
image_data = recvall(conn, length)

# Converti in array numpy
nparr = np.frombuffer(image_data, np.uint8)

# Decodifica in immagine
img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# Mostra immagine
cv2.imshow("Ricevuta", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
