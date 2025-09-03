from enum import Enum


class Command(Enum):
    PING = "PING"


class UnsupportedCommandError(Exception):
    pass


def handle_command(cmd: list[str]) -> str:
    if len(cmd) == 1:
        try:
            command = Command(cmd[0])
        except ValueError as e:
            msg = f"Command {cmd} is not supported"
            raise UnsupportedCommandError(msg) from e

        if command is Command.PING:
            return _handle_ping()

    msg = f"Command {cmd} is not supported"
    raise UnsupportedCommandError(msg)


def _handle_ping() -> str:
    return "PONG"
