import cv2
import csv
import numpy as np
import pandas as pd
import os
file_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\Data\sensor_data_11.csv"

data = pd.read_csv(file_path)

# readings_dict = {row['Time(s)']: (row["R1(O)"], 
#                                    row["R2(O)"], 
#                                    row["R3(O)"], 
#                                    row["R4(O)"]) for _, row in data.iterrows()}

readings_list = data.values.tolist()

video_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\data_11_edited.mp4"
cap = cv2.VideoCapture(video_path)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

output_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\output_vid_w_resistance.avi"
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc=fourcc, fps=fps, frameSize=(width, height))

frame_count = 0
reading_index = 20
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    if reading_index < len(readings_list):
        curr_time, r1, r2, r3, r4 = readings_list[reading_index]

        frame_time = frame_count/fps
        if frame_time >= curr_time:

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (0,255,0)
            thickness = 2

            cv2.putText(frame, f"Time: {curr_time:.2f}s", (10,50), font, font_scale,
                        font_color, thickness, cv2.LINE_AA)

            cv2.putText(frame, f"R1: {r1} Ohms", (10,100), font, font_scale,
                        font_color, thickness, cv2.LINE_AA)
            cv2.putText(frame, f"R2: {r2} Ohms", (10,150), font, font_scale,
                        font_color, thickness, cv2.LINE_AA)
            cv2.putText(frame, f"R3: {r3} Ohms", (10,200), font, font_scale,
                        font_color, thickness, cv2.LINE_AA)
            cv2.putText(frame, f"R4: {r4} Ohms", (10,250), font, font_scale,
                        font_color, thickness, cv2.LINE_AA)
            
            reading_index += 1
        
    cv2.imshow('Video with resistance overlay', frame)

    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1

cap.release()
out.release()
cv2.destroyAllWindows()
