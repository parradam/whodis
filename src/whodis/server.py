import socket
from typing import cast

from src.whodis.commands import UnsupportedCommandError, handle_command
from src.whodis.deserialise import InvalidMessageError, deserialise
from src.whodis.serialise import Kind, SerialiseError, serialise
from src.whodis.shared import RESPDataType

HOST = ""
PORT = 6379


def run_server() -> None:
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print("Server running on port", PORT)

        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break  # client disconnected
                    response = _handle_request(data)
                    print(response)
                    conn.sendall(response)


def _handle_request(data: bytes) -> bytes:
    try:
        deserialised = deserialise(data.decode()).data
    except UnicodeDecodeError:
        return serialise("ERR invalid encoding", kind=Kind.ERROR).message.encode()
    except InvalidMessageError:
        return serialise("ERR invalid request", kind=Kind.ERROR).message.encode()

    try:
        normalised = _normalise_input(deserialised)
    except TypeError:
        return serialise("ERR command must be an array of strings", kind=Kind.ERROR).message.encode()

    try:
        handled = handle_command(normalised)
    except UnsupportedCommandError:
        return serialise("ERR unsupported command", kind=Kind.ERROR).message.encode()

    # PING/PONG is a special case where PING could be sent as a simple
    # string or a bulk string, but the response should be a simple string
    kind = Kind.PROTOCOL if handled == "PONG" else Kind.NON_PROTOCOL
    try:
        return serialise(handled, kind=kind).message.encode()
    except SerialiseError:
        return serialise("ERR serialisation failed", kind=Kind.ERROR).message.encode()


def _normalise_input(data: RESPDataType) -> list[str]:
    if isinstance(data, str):
        data = [data]
    if not isinstance(data, list) or not all(isinstance(d, str) for d in data):
        msg = "Data is not a list of strings"
        raise TypeError(msg)
    return cast("list[str]", data)

if __name__ == "__main__":
    run_server()
