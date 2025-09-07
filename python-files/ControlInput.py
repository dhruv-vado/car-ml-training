import socket
import time

HOST = '127.0.0.1'
CONTROL_PORT = 65433

def send_control(sock, steer, throttle, brake):
    msg = f"{steer},{throttle},{brake}\n"
    sock.sendall(msg.encode('ascii'))

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as control_sock:
        print(f"Connecting to control server at {HOST}:{CONTROL_PORT}...")
        control_sock.connect((HOST, CONTROL_PORT))
        print("Connected. Sending control commands...")
        try:
            while True:
                # Example: always go forward
                steer = 0.5
                throttle = 1.0
                brake = 0.0
                send_control(control_sock, steer, throttle, brake)
                time.sleep(0.01)  # Send commands at 10Hz
        except KeyboardInterrupt:
            print("Exiting control input script.") 