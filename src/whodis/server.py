import socket
import threading
from typing import cast

from src.whodis.commands import UnsupportedCommandError, handle_command
from src.whodis.deserialise import InvalidMessageError, deserialise
from src.whodis.serialise import Kind, SerialiseError, serialise
from src.whodis.shared import RESPDataType


class WhodisServer:
    def __init__(self, host: str = "", port: int = 6379) -> None:
        self.host = host
        self.port = port
        self._bound_port: int | None = None
        self._stop_event = threading.Event()
        self.server_ready = threading.Event()
        self._server_thread: threading.Thread | None = None

    def start(self) -> None:
        self._server_thread = threading.Thread(target=self._run, daemon=True)
        self._server_thread.start()
        self.server_ready.wait(timeout=1)

    def stop(self) -> None:
        self._stop_event.set()
        if self._server_thread is not None:
            self._server_thread.join(timeout=1)

    @property
    def bound_port(self) -> int:
        if self._bound_port is None:
            msg = "Server not started"
            raise RuntimeError(msg)

        return self._bound_port

    def _run(self) -> None:
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            self._bound_port = s.getsockname()[1]
            s.listen(5)
            print(f"Server running on port {self._bound_port}")
            self.server_ready.set()

            s.settimeout(0.5)
            while not self._stop_event.is_set():
                try:
                    conn, addr = s.accept()
                except TimeoutError:
                    continue

                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break  # client disconnected

                        response = self._handle_request(data)
                        conn.sendall(response)

    def _handle_request(self, data: bytes) -> bytes:
        try:
            deserialised = deserialise(data.decode()).data
        except UnicodeDecodeError:
            return serialise("ERR invalid encoding", kind=Kind.ERROR).message.encode()
        except InvalidMessageError:
            return serialise("ERR invalid request", kind=Kind.ERROR).message.encode()

        try:
            normalised = self._normalise_input(deserialised)
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

    def _normalise_input(self, data: RESPDataType) -> list[str]:
        if isinstance(data, str):
            data = [data]

        if not isinstance(data, list) or not all(isinstance(d, str) for d in data):
            msg = "Data is not a list of strings"
            raise TypeError(msg)

        return cast("list[str]", data)


if __name__ == "__main__":
    server = WhodisServer()
    server.start()
