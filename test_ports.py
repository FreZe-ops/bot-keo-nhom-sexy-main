import socket

HOST = '180.93.235.84'
ports = [22, 55293, 3389, 2222]

for p in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    res = s.connect_ex((HOST, p))
    s.close()
    print(f"Port {p}: {'OPEN' if res == 0 else 'CLOSED'}")
