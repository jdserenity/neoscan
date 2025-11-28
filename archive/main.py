import socket

# ip = "127.0.0.1"
ip = "scanme.nmap.org"
port = 22

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
result = sock.connect_ex((ip, port))

if result == 0:
    print(f"Port {port} is OPEN on {ip}")
else:
    print(f"Port {port} is closed/filtered (error code {result})")

sock.close()
