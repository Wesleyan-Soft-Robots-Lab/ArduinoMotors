import cv2
import numpy as np
import math

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
    # Find contours of the black dots
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size (to exclude noise)
    dot_positions = []
    for contour in contours:
        if cv2.contourArea(contour) > 5:  # Example size threshold
            # Get the center of the dot
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                dot_positions.append((cx, cy))
    
    # Calculate the center of the object (assuming it's the geometric center of the dots)
    if len(dot_positions) == 2:
        (x1, y1), (x2, y2) = dot_positions
        angle = math.degrees(math.atan2(y2-y1, x2 - x1))
        cv2.circle(frame, (x1,y1), 5, (0, 255, 0), -1)
        cv2.circle(frame, (x2,y2), 5, (0, 255, 0), -1)
        cv2.line(frame, (x1, y1), (x2,y2), (255, 0,0),2)
        cv2.putText(frame, f"Angle: {angle:.1f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return frame, angle
    else:

        return frame, None

def analyze_video(video_path):
    """
    Analyze video frames to detect black dots and calculate angles for each frame.
    """
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    output_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\output_angle.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc=fourcc, fps=fps, frameSize=(width, height))

    angles = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process each frame
        processed_frame, angle = process_frame(frame)
        # processed_frame = cv2.resize(processed_frame, (width, height))
        out.write(processed_frame)
        # Print the angles for this frame
        # print(f"Angles: {[(x, y, angle) for x, y, angle in angles]}")
        if angle is not None:
            print(f"Angle between the dots: {angle:.2f} degrees")
            angles.append(angle)
        # Display the processed frame
        cv2.imshow("Processed Frame", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    return angles, output_path
    # cv2.destroyAllWindows()

path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\data_12.mp4"
angles,output_path =  analyze_video(path)
angles, output_path
