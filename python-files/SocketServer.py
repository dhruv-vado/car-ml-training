import socket

HOST = '127.0.0.1'   # Localhost (use real IP for remote)
PORT = 65432         # Port to listen on

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print('Waiting for Unity to connect...')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print('Received:', data.decode())
            response = 'ACK from Python'
            conn.sendall(response.encode())
