import os
import cv2 as cv
from pydantic import BaseModel

from src.processing.proctoring.face_detection import FaceDetection
from src.processing.proctoring.gaze_detection import GazeDetection

    
def load_images_from_folder(folder_path):
    images = []
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp"}  # Supported image extensions
    for filename in os.listdir(folder_path):
        # Check file extension to confirm it's an image
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_extensions:
            print(f"Skipping non-image file: {filename}")
            continue

        # Construct the full file path
        file_path = os.path.join(folder_path, filename)

        # Read the image and add to list if it's loaded successfully
        image = cv.imread(file_path)
        if image is not None:
            images.append([filename,image])
        else:
            print(f"Unable to load image: {file_path}")
    return images

def processFrame():

    # Use dynamic path based on the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, "test_images")

    # Check if the directory exists
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []
    
    frames_data = load_images_from_folder(folder_path)
    
    gaze_detection = GazeDetection()
    face_detection = FaceDetection()
    
    continuous_gaze_out_count = 3
    gaze_out_data = []
    suspicious_behaviors = []  # To store timestamps of suspicious behaviors
    for meta in frames_data:
        filename,image = meta
        try:
            # Process the image for head pose and gaze detection
            finalGaze = gaze_detection.processGaze(image)
            if finalGaze == 'out':
                continuous_gaze_out_count -= 1
                gaze_out_data.append(filename)
                if (continuous_gaze_out_count == 0):
                    suspicious_behaviors.append({"flag": "gaze_out","frames": gaze_out_data})
                    
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
                suspicious_behaviors.append({"flag": "absence","frames": [filename]})
            elif faceCount >1:
                suspicious_behaviors.append({"flag": "multiple_face","frames":[filename]})
        except Exception as e:
            print(f"Error in face detection: {e}")
    return suspicious_behaviors