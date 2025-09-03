import socket

import pytest

from src.whodis.server import WhodisServer


@pytest.mark.parametrize(
    "message",
    [
        pytest.param(b"+PING\r\n", id="server_simple_ping"),
        pytest.param(b"$4\r\nPING\r\n", id="server_bulk_ping"),
    ],
)
def test_ping_response(message: bytes) -> None:
    server = WhodisServer(host="", port=0)
    server.start()

    with socket.create_connection(("127.0.0.1", server.bound_port)) as s:
        s.sendall(message)
        response = s.recv(1024)

    server.stop()

    assert response == b"+PONG\r\n"
