import cv2 as cv
import numpy as np
import requests

from src.processing.proctoring.face_detection import FaceDetection
from src.processing.proctoring.gaze_detection import GazeDetection

def processFrame(frame_urls: list):
    
    gaze_detection = GazeDetection()
    face_detection = FaceDetection()
    
    continuous_gaze_out_count = 3
    gaze_out_data = []
    suspicious_behaviors = [] 
    for image_url in frame_urls:
        image = requests.get(image_url)
        
        if image.status_code != 200 or image.content == b'':
            print("content issue")
            continue
        
        image_np = np.frombuffer(image.content, np.uint8)
        image = cv.imdecode(image_np, cv.IMREAD_COLOR)
        try:
            
            # Process the image for head pose and gaze detection
            finalGaze = gaze_detection.processGaze(image)
            if finalGaze == 'out':
                continuous_gaze_out_count -= 1
                gaze_out_data.append(image_url)
                if (continuous_gaze_out_count == 0):
                    suspicious_behaviors.append({"tag": "gaze_out","frames": gaze_out_data})
                    
                    #reset count an image list
                    continuous_gaze_out_count = 3
                    gaze_out_data = []
            else:
                continuous_gaze_out_count = 3
                gaze_out_data = []
        except Exception as e:
            print(f"Error in gaze detection: {e}")
            
        try:
            faceCount = face_detection.faceCountDetection(image)
            if faceCount == 0:
                suspicious_behaviors.append({"tag": "absence","frames": [image_url]})
            elif faceCount >1:
                suspicious_behaviors.append({"tag": "multiple_face","frames":[image_url]})
        except Exception as e:
            print(f"Error in face detection: {e}")

    return suspicious_behaviors