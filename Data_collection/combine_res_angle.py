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
    # mask = cv2.imshow("mask", mask)
    # Find contours of the black dots
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size (to exclude noise)
    dot_positions = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Example size threshold
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

    # Separate visual frame to show mask
    # mask_show = cv2.imshow("mask", mask)
    
    # Calculate the center of the object (assuming it's the geometric center of the dots)
    if len(dot_positions) == 2: # If 2 dots on machine
        (x1, y1), (x2, y2) = dot_positions
        angle = math.degrees(math.atan2(y1-y2, x1 - x2))
        angle = round(angle,2)
        cv2.circle(frame, (x1,y1), 5, (0, 255, 0), -1)
        cv2.circle(frame, (x2,y2), 5, (0, 255, 0), -1)
        cv2.line(frame, (x1, y1), (x2,y2), (255, 0,0),2)
        cv2.putText(frame, f"Angle: {angle:.1f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame, (angle,None)
    elif len(dot_positions) == 3: # If 3 dots on machine
        '''
        Please note that this should work assuming the third dot is always at a
        lower y position than the second (which I believe it should be) --Simon
        '''
        [(x1,y1), (x2,y2), (x3,y3)] = dot_positions
        # print(dot_positions)
        angle1 = math.degrees(math.atan2(y1-y2,x1-x2))
        angle1 = round(angle1,2)
        angle2 = math.degrees(math.atan2(y2-y3,x2-x3))
        angle2 = round(angle2,2)
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

def analyze_video(video_path):
    """
    Analyze video frames to detect red dots and calculate angles for each frame.
    """
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    output_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\output_angle.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc=fourcc, fps=fps, frameSize=(width, height))
    frame_count = 0
    reading_index = 0
    data = pd.DataFrame(columns = ['Time(s)',
                                   'R1(O)', 
                                   'R2(O)',
                                   'R3(O)',
                                   'R4(O)',
                                   'Angle1(deg)',
                                   'Angle2(deg)'])
    time_file = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\Data\sensor_data_18.csv"
    data_time = pd.read_csv(time_file)
    readings_list = data_time.values.tolist()
    # start_time = time.time()

    angles1 = []
    angles2 = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process each frame
        processed_frame, (angle1,angle2) = process_frame(frame)
        # processed_frame = cv2.resize(processed_frame, (width, height))
        out.write(processed_frame)
        # Print the angles for this frame
        # Append angles to respective lists
        if angle1 is not None:
            angles1.append(angle1)
        if angle2 is not None:
            angles2.append(angle2)

        # Create new line of data
        # timed = time.time() - start_time
        # timed = round(timed,1)
        # print(len(readings_list), reading_index)
        if reading_index < len(readings_list):
            init_time,_,_,_,_ = readings_list[0]
            curr_time, r1, r2, r3, r4 = readings_list[reading_index]
            frame_time = frame_count/fps + init_time
            # print(frame_time, curr_time)
            if frame_time >= curr_time:
                new_row = pd.DataFrame({'Time(s)': [curr_time],
                                        'R1(O)': [r1],
                                        'R2(O)': [r2],
                                        'R3(O)': [r3],
                                        'R4(O)': [r4],
                                        'Angle1(deg)': [angle1],
                                        'Angle2(deg)': [angle2]})
                data = pd.concat([data,new_row], ignore_index=True)
                reading_index += 1
        frame_count += 1
        # Display the processed frame
        cv2.imshow("Processed Frame", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

    cap.release()
    out.release()
    
    # Convert to csv
    if len(data) == 0:
        print("No Data Saved")
    else:
        dir_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\Angle_Data"
        files = os.listdir(dir_path)
        i = len(files)
        data.to_csv(f'Data_collection\Angle_Data\\angle_data_{i}.csv', index=False)
        print(f"Data saved to 'angle_data_{i}.csv'.")

    return angles1,angles2, output_path
    # cv2.destroyAllWindows()

# Path for full image:
path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\output.avi"
# Path for partial image:
# path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\data_12.mp4"
angles1,angles2,output_path =  analyze_video(path)

