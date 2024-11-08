import cv2 as cv
import numpy as np
import mediapipe as mp
import math

class GazeDetection:

    def __init__(self):
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True
        )

    def _detectHeadPose(self, image, results):
        orientation = "Unknown"  # Default value in case head pose is not detected
        
        img_h, img_w, img_c = image.shape

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                face_2d = []
                face_3d = []

                for idx, lm in enumerate(face_landmarks.landmark):
                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    if idx == 1:
                        nose_2d = (x, y)
                        nose_3d = (x, y, lm.z * 3000)

                    if idx in [33, 263, 1, 61, 291, 199]:
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])

                face_2d = np.array(face_2d, dtype=np.float64)
                face_3d = np.array(face_3d, dtype=np.float64)

                # Camera matrix
                focal_length = 1 * img_w
                cam_matrix = np.array([[focal_length, 0, img_w / 2],
                                       [0, focal_length, img_h / 2],
                                       [0, 0, 1]])

                # Distortion parameters
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # SolvePnP
                success, rot_vec, trans_vec = cv.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Rotation matrix
                rmat, _ = cv.Rodrigues(rot_vec)

                # Angles
                angles, _, _, _, _, _ = cv.RQDecomp3x3(rmat)
                x_angle = angles[0] * 360
                y_angle = angles[1] * 360

                slight_horizontal_threshold = 15
                major_horizontal_threshold = 20
                # Determine the orientation
                if -major_horizontal_threshold < y_angle < -slight_horizontal_threshold:
                    orientation = "left"
                elif slight_horizontal_threshold < y_angle < major_horizontal_threshold :
                    orientation = "right"
                elif y_angle < -major_horizontal_threshold or y_angle > major_horizontal_threshold:
                    orientation = 'out'
                elif x_angle < -10:
                    orientation = "down"
                elif x_angle > 20:
                    orientation = "up"
                else:
                    orientation = "forward"

        return orientation
    
    def _euclidean_distance(self,point1,point2):
        x1,y1 = point1.ravel()
        x2,y2 = point2.ravel()
        return math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def _iris_position_ratio(self,iris_centre, right_point,left_point):
        centre_to_right_dist = self._euclidean_distance(iris_centre,right_point)
        total_distance = self._euclidean_distance(right_point,left_point)
            
        return centre_to_right_dist/total_distance

    def _detectEyeGaze(self, image, results):
        eye_gaze = "Unknown"  # Default value if eye gaze is not detected
        left_iris = [469, 470, 471, 472]
        right_iris = [474, 475, 476, 477]
        left_eye_ext_points = [33, 133]
        right_eye_ext_points = [362, 263]
        
        img_h, img_w, = image.shape[:2]
        
        if results.multi_face_landmarks:
            
            mesh_points = np.array([np.multiply([p.x, p.y],[img_w,img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])

            (l_cx,l_cy), l_radius = cv.minEnclosingCircle(mesh_points[left_iris])
            (r_cx,r_cy), r_radius = cv.minEnclosingCircle(mesh_points[right_iris])
            left_centre = np.array([l_cx,l_cy], dtype=np.int32)
            right_centre = np.array([r_cx,r_cy], dtype=np.int32)
            
            # cv.circle(image,left_centre,int(l_radius), (0,0,255),1,cv.LINE_AA)
            # cv.circle(image,right_centre,int(r_radius), (0,0,255),1,cv.LINE_AA)
            
            left_iris_position_ratio = self._iris_position_ratio(left_centre,mesh_points[left_eye_ext_points[1]], mesh_points[left_eye_ext_points[0]])
            right_iris_position_ratio = self._iris_position_ratio(right_centre,mesh_points[right_eye_ext_points[1]],mesh_points[right_eye_ext_points[0]])
            
            # cv.putText(image,f'ration: {left_iris_position_ratio}',(120,50),cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 2)
            combined_avg_ratio = (left_iris_position_ratio + right_iris_position_ratio)/2.0
            
            left_threshold = 0.62
            right_threshold = 0.42
            gaze = "centre"
            
            if combined_avg_ratio > left_threshold:
                gaze = "left"
            elif combined_avg_ratio < right_threshold:
                gaze = "right"
        return gaze

    def processGaze(self, image):
        # Process the image once and pass results to both functions
        flipped_image = cv.flip(image,1)
        image_rgb = cv.cvtColor(flipped_image, cv.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        # Detect head pose and eye gaze using the same results
        headPose = self._detectHeadPose(image, results)
        eyeGaze = self._detectEyeGaze(image, results)
        
        finalGaze = 'centre'
        
        if headPose == 'forward':
            if eyeGaze == 'left' or eyeGaze == 'right':
                finalGaze = 'out'
        elif headPose == 'left':
            if eyeGaze == 'centre':
                finalGaze = 'out'
        elif headPose == 'right':
            if eyeGaze == 'centre':
                finalGaze = 'out'
        elif headPose == 'out':
            finalGaze = 'out'
            
        return finalGaze
    
