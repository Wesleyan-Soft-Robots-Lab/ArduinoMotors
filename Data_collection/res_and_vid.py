import cv2
import serial
import threading
import time
import pandas as pd
import os

start_event = threading.Event()
stop_event = threading.Event()
dir_path = r"C:\Users\softrobotslab\ArduinoMotors\Data_collection\Data"
files = os.listdir(dir_path)

def capture_video(output):
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print('Error with accessing the camera.')
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f'Camera resolution set to: {width}x{height}')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output, fourcc, 20.0, (1920,1080))
    print('Waiting to start video recording...')
    start_event.wait()
    print('Recording')
    while not stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break
        else:
            print('error reading frame')
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Recording stopped")

def read_resistance(port, baudrate):
    data = pd.DataFrame(columns=['Time(s)',
                                 'R1(O)',
                                 'R2(O)',
                                 'R3(O)',
                                 'R4(O)'])
    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
        print('waiting to start serial readings...')
        start_event.wait()
        print('Serial connection established')
        while not stop_event.is_set():
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                parts = line.split()
                timed = time.time()
                r1 = parts[1]
                r2 = parts[2]
                r3 = parts[3]
                r4 = parts[4]
                print(f'Serial data: {timed, r1, r2, r3, r4}')
                new_row = pd.DataFrame({'Time(s)': [timed],
                                        'R1(O)': [r1],
                                        'R2(O)': [r2],
                                        'R3(O)': [r3],
                                        'R4(O)': [r4]
                                        })
                data = pd.concat([data, new_row], ignore_index=True)
            # time.sleep(0.01)
        print('serial readings stopped')
        ser.close()
    except serial.SerialException as e:
        print(f'Serial Error: {e}')
    finally:
        if len(data) == 0:
            print("No Data saved")
            pass
        else:
            # Save to CSV when the script ends
            i = len(files)
            data.to_csv(f'Data_collection\Data\sensor_data_{i}.csv', index=False)
            print(f"Data saved to 'sensor_data_{i}.csv'.")

if __name__ == '__main__':

    # running = True

    output = r'C:\Users\softrobotslab\ArduinoMotors\Data_collection\output.avi'

    video_thread = threading.Thread(target=capture_video, args=(output,))
    serial_thread = threading.Thread(target=read_resistance, args=('COM5', 9600))
    video_thread.start()
    serial_thread.start()

    try:
        print('Initializing...')
        time.sleep(1)
        start_event.set()
        video_thread.join()
        serial_thread.join()

    except KeyboardInterrupt:
        print('Stopping...')
        stop_event.set()
        video_thread.join()
        serial_thread.join()
        print('All finished')

    



