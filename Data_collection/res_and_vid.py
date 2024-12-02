import cv2
import serial
import threading
import time

def capture_video(output):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print('Error with accessing the camera.')
        return
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output, fourcc, 20.0, (640,480))

    print('Recording')
    while running:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('qq'):
                break
        else:
            print('error reading frame')
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Recording stopped")

def read_resistance(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print('Serial connection established')
        while running:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').strip()
                print(f'Serial data: {data}')
            time.sleep(0.01)
    except serial.SerialException as e:
        print(f'Serial Error: {e}')

if __name__ == '__main__':

    running = True

    output = 'output.avi'

    video_thread = threading.Thread(target=capture_video, args=(output,))
    serial_thread = threading.Thread(target=read_resistance, args=('COM5', 9600))
    video_thread.start()
    serial_thread.start()

    try:
        video_thread.join()
        serial_thread.join()

    except KeyboardInterrupt:
        print('Stopping...')
        running = False
        video_thread.join()
        serial_thread.join()
        print('All finished')



