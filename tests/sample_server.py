# Echo server program
import socket

HOST = 'localhost'                 # Symbolic name meaning all available interfaces
PORT = 1024               # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
print('server starts listening')
s.listen()
conn, addr = s.accept()
print('server accepts connection')
data = conn.recv(1234)
print(f'server receives {data}')
conn.close()
s.close()
print('server exits')
