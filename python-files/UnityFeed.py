import socket
import struct
import numpy as np
import cv2
import time
import csv
import os

HOST = '127.0.0.1'
CAMERA_PORT = 65432

def receive_multi_camera_frames():
    output_dir = 'images'
    os.makedirs(output_dir, exist_ok=True)
    csv_file = open('controls.csv', 'a', newline='')
    csv_writer = csv.writer(csv_file)
    if os.path.getsize('controls.csv') == 0:
        csv_writer.writerow(['center_frame', 'left_frame', 'right_frame', 'steer', 'throttle', 'brake'])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, CAMERA_PORT))
        s.listen(1)
        print('Waiting for Unity...')
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            pTime = 0
            frame_count = 0
            while True:
                frame_files = []
                imgs = []
                # --- Receive three camera images (center, left, right) ---
                for label in ['center', 'left', 'right']:
                    length_bytes = conn.recv(4)
                    if not length_bytes:
                        break
                    img_len = struct.unpack('I', length_bytes)[0]
                    data = b''
                    while len(data) < img_len:
                        packet = conn.recv(img_len - len(data))
                        if not packet:
                            break
                        data += packet
                    img_array = np.frombuffer(data, np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    filename = f"{label}_{frame_count:05d}.jpg"
                    cv2.imwrite(os.path.join(output_dir, filename), frame)
                    frame_files.append(filename)
                    imgs.append(frame)
                if len(imgs) < 3:
                    break

                # Show center frame with FPS
                cTime = time.time()
                fps = 1/(cTime-pTime) if (cTime-pTime) > 0 else 0
                pTime = cTime
                cv2.putText(imgs[0], str(int(fps)), (10, 70),
                            cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                cv2.imshow('Unity Center Frame', imgs[0])
                frame_count += 1

                # --- Receive controls line ---
                ctrl_line = b''
                while not ctrl_line.endswith(b'\n'):
                    chunk = conn.recv(1)
                    if not chunk:
                        break
                    ctrl_line += chunk
                try:
                    steer, throttle, brake = map(float, ctrl_line.decode().strip().split(','))
                except Exception as e:
                    print(f"Ctrl parse error: {e}, line={ctrl_line}")
                    steer, throttle, brake = 0.0, 0.0, 0.0

                csv_writer.writerow([frame_files[0], frame_files[1], frame_files[2], steer, throttle, brake])
                csv_file.flush()

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    csv_file.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    receive_multi_camera_frames()
