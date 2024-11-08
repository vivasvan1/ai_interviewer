import cv2 as cv
import mediapipe as mp

class FaceDetection:
    
    def __init__(self):
        mp_faceDetector = mp.solutions.face_detection
        self.face_detection = mp_faceDetector.FaceDetection(min_detection_confidence=0.5)
        
    def faceCountDetection(self,image):
        image = cv.cvtColor(image,cv.COLOR_BGR2RGB)
        results = self.face_detection.process(image)
        
        if results.detections:
            count = len(results.detections)
        else:
            count = 0
        return count
        
                
            
            

