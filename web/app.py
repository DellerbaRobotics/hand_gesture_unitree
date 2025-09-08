from flask import Flask, Response
import cv2
import numpy as np
import mmap

app = Flask(__name__)

### CONSTANTS
FRAME_PATH = "/stream/frame.raw"
FRAMESIZE_FILE_PATH = "/stream/framesize.txt"

with open(FRAMESIZE_FILE_PATH, "r") as f:
    width, height = map(int, f.readline().split(" "))
frame_size = width * height * 3

def udp_video_receiver():
    with open(FRAME_PATH, "r+b") as f:
        mm = mmap.mmap(f.fileno(), frame_size, access=mmap.ACCESS_READ)

        last_frame = None
        while True:
            try:
                mm.seek(0)
                data = mm.read(frame_size)
                frame = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 3))

                if last_frame is not None and np.array_equal(frame, last_frame):
                    continue
                last_frame = frame

                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
            except Exception as e:
                print("Errore ricezione:", e)
                break


@app.route('/video')
def video():
    return Response(udp_video_receiver(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)