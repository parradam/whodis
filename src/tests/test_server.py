import socket
import threading
import time

from src.whodis.server import HOST, PORT, run_server


def start_server() -> None:
    run_server()

def test_ping_response() -> None:
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    with socket.create_connection((HOST, PORT)) as s:
        s.sendall(b"+PING\r\n")
        response = s.recv(1024)

    assert response == b"+PONG\r\n"
