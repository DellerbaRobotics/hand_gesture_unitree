#### Flask app to stream video frames read from a memory-mapped file.
## The frames are read from a file specified by FRAME_PATH, which is memory-mapped for efficient access.
## The frame size (width and height) is read from a separate file specified by FRAMESIZE_FILE_PATH.
## The app defines a single route '/video' that streams the video frames as a multipart HTTP response.
## The video frames are encoded as JPEG images using OpenCV before being sent to the client.

from flask import Flask, Response # Import the Flask web framework and Response object for HTTP responses
import numpy as np # Import NumPy for efficient array manipulation
import mmap # Import mmap for memory-mapped file access
import cv2 # Import OpenCV for image encoding and processing

app = Flask(__name__) # Create a Flask application instance

### CONSTANTS
FRAME_PATH = "/stream/frame.raw"
FRAMESIZE_FILE_PATH = "/stream/framesize.txt"

# Open the file containing the frame size (width and height) in read mode
with open(FRAMESIZE_FILE_PATH, "r") as f:
    try:
        # Read the first line, strip whitespace, split by space, convert both values to integers, and assign to width and height
        width, height = map(int, f.readline().strip().split(" "))
    except:
        # If any error occurs (e.g., file format issue), exit the program with status 1
        exit(1)

frame_size = width * height * 3 # 3 bytes per pixel for RGB

def video_receiver():
    """
    Generator function that reads video frames from a memory-mapped file and yields them as JPEG-encoded byte streams.
    The function opens a file specified by FRAME_PATH in read/write binary mode, memory-maps it, and continuously reads
    frames of size `frame_size`. Each frame is reshaped into a NumPy array with dimensions `(height, width, 3)` representing
    an RGB image. If the current frame is identical to the previous frame, it is skipped to avoid redundant processing.
    Otherwise, the frame is JPEG-encoded using OpenCV and yielded in a multipart HTTP response format suitable for streaming.
    Yields:
        bytes: A multipart HTTP response containing the JPEG-encoded image.
    Raises:
        Exception: If an error occurs during frame reading or processing, the exception is printed and the generator stops.
    """
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
    return Response(video_receiver(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)