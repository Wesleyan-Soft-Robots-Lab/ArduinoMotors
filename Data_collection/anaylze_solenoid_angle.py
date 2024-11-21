import cv2
import numpy as np
import math

def process_frame(frame):
    """
    Analyze a frame to detect black dots and calculate their angles relative to the center.
    """
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Threshold the image to isolate black dots (assume black dots are darker than 50 intensity)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours of the black dots
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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
    if len(dot_positions) > 1:
        center_x = int(np.mean([pos[0] for pos in dot_positions]))
        center_y = int(np.mean([pos[1] for pos in dot_positions]))
    else:
        center_x, center_y = 0, 0  # Fallback if no dots detected
    
    # Calculate angles of each dot relative to the center
    angles = []
    for (x, y) in dot_positions:
        angle = math.degrees(math.atan2(y - center_y, x - center_x))
        angles.append((x, y, angle))
    
    # Annotate the frame with the results
    for (x, y, angle) in angles:
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Draw dot
        cv2.line(frame, (center_x, center_y), (x, y), (255, 0, 0), 1)  # Line to center
        cv2.putText(frame, f"{angle:.1f}", (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # Draw center

    return frame, angles

def analyze_video(video_path):
    """
    Analyze video frames to detect black dots and calculate angles for each frame.
    """
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process each frame
        processed_frame, angles = process_frame(frame)
        
        # Print the angles for this frame
        print(f"Angles: {[(x, y, angle) for x, y, angle in angles]}")
        
        # Display the processed frame
        cv2.imshow("Processed Frame", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


analyze_video("data_8_trim.mp4")
