from typing import List
import cv2
import logging

CAMERAS: List[cv2.VideoCapture] = []


def start_cameras(max_cams: int = 3):
    """Open available cameras up to max_cams and store in CAMERAS."""
    for i in range(max_cams):
        cam = cv2.VideoCapture(i)
        if cam.isOpened():
            CAMERAS.append(cam)
            logging.info(f"Camera {i} opened")
        else:
            logging.info(f"Camera {i} could not be opened")


def gen_frames(cam_index: int):
    cam = CAMERAS[cam_index]
    while True:
        success, frame = cam.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
