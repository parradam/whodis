COMMANDS = {
    "PING",
}


class UnsupportedCommandError(Exception):
    pass


def handle_command(cmd: list[str]) -> str:
    if len(cmd) == 1 and cmd[0] == "PING":
        return _handle_ping()

    msg = f"Command {cmd} is not supported"
    raise UnsupportedCommandError(msg)


def _handle_ping() -> str:
    return "PONG"
