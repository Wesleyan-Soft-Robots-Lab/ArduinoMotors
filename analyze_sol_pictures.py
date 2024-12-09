import cv2
import numpy as np
import math
import pandas as pd
import time
import os

def process_frame(frame):
    """
    Analyze a frame to detect black dots and calculate their angles relative to the center.
    """
    # Convert the frame to grayscale
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Threshold the image to isolate black dots (assume black dots are darker than 50 intensity)
    # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    lower_red1 = np.array([0,120,70])
    upper_red1 = np.array([10,255,255])
    lower_red2 = np.array([170,120,70])
    upper_red2 = np.array([180,255,255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.GaussianBlur(mask, (5,5),0)
    # Separate visual frame to show mask
    # mask_img = cv2.imshow("mask", mask)
    # Find contours of the black dots
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Filter contours by size (to exclude noise)
    dot_positions = []

    for contour in contours:
        
        #im not exactly sure if 250 is the correct threshold
        if cv2.contourArea(contour) > 250:  # Example size threshold
            (cx, cy), r = cv2.minEnclosingCircle(contour)
            r = int(r)
            # Determine whether dot is circle
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue
            circ = 4 * np.pi * (area/(perimeter**2))
            # If circle, add to dot list.
            if circ >= 0.7 and circ <= 1.3:   
                dot_positions.append((int(cx),int(cy)))
                cv2.circle(frame,(int(cx),int(cy)),r,(0,255,255),2)

    # Calculate the center of the object (assuming it's the geometric center of the dots)
    if len(dot_positions) == 2: # If 2 dots on machine
        (x1, y1), (x2, y2) = dot_positions
        angle = 90 - math.degrees(math.atan2(y1-y2, x1 - x2))
        angle = round(angle,2)
        cv2.circle(frame, (x1,y1), 5, (0, 255, 0), -1)
        cv2.circle(frame, (x2,y2), 5, (0, 255, 0), -1)
        cv2.line(frame, (x1, y1), (x2,y2), (255, 0,0),2)
        cv2.putText(frame, f"Angle: {angle:.1f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame, (angle,None)
    elif len(dot_positions) == 3: # If 3 dots on machine
        '''
        Please note that this should work assuming the second dot is always at a
        lower y position than the third (which I believe it should be) --Simon
        '''
        [(x1,y1), (x2,y2), (x3,y3)] = dot_positions
        
        angle1 = 90 - math.degrees(math.atan2(y1-y2,x1-x2))
        angle1 = round(angle1,2)
        angle2 = 90 - math.degrees(math.atan2(y2-y3,x2-x3))
        angle2 = round(angle2,2)
        angle1 -= angle2
        cv2.circle(frame, (x1,y1), 5, (0, 255, 0), -1)
        cv2.circle(frame, (x2,y2), 5, (0, 255, 0), -1)
        cv2.circle(frame, (x3,y3), 5, (0, 255, 0), -1)
        cv2.line(frame, (x1,y1), (x2,y2), (255, 0, 0),2)
        cv2.line(frame, (x2,y2), (x3,y3), (255, 0, 0), 2)
        cv2.putText(frame, f"Angle 1: {angle1:.1f}", (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        cv2.putText(frame, f"Angle 2: {angle2:.1f}", (x2,y2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame, (angle1, angle2)
    
    else:
        return frame, (None, None)


def analyze_pictures(img_folder):
    data = pd.DataFrame(columns=[
                                   'Angle1(deg)',
                                   'Angle2(deg)',
                                   'imageNum'    
                                ])

    for filename in os.listdir(img_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            [_,index, _] = filename.split("_")

            img_path = os.path.join(img_folder, filename)

            image = cv2.imread(img_path)

            _,(a1, a2) = process_frame(image)
            new_row = pd.DataFrame({
                                 'Angle1(deg)': [a1],
                                 'Angle2(deg)': [a2],
                                 'imageNum': [int(index)]})
            
            data = pd.concat([data, new_row])

    data = data.sort_values(by= 'imageNum', ascending= True)
    data.to_csv('angles_output.csv', index=False)
    return 

#analyze_pictures(r"C:\Users\softrobotslab\ArduinoMotors\TestData")

#personal dir. Comment out/delete
analyze_pictures(r"C:\Users\miles\Documents\GitHub\ArduinoMotors\TestData")