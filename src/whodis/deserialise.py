# Defines carriage return/line feed, used as a terminator and a delimiter
CRLF = "\r\n"

class InvalidMessageError(ValueError):
    pass

def parse_simple_string(line: str) -> str:
    # Cannot accept only one char (the prefix)
    if len(line) == 1:
        raise InvalidMessageError
    return line[1:]

def parse_integer(line: str) -> int:
    # Cannot accept only one char (the prefix)
    if len(line) == 1:
        raise InvalidMessageError
    try:
        return int(line[1:])
    except ValueError as e:
        raise InvalidMessageError from e

def parse(lines: list[str]) -> str | int:
    # The following parsers expect only one line
    if len(lines) != 1:
        raise InvalidMessageError

    line = lines[0]
    if line.startswith("+"):
        return parse_simple_string(line)
    if line.startswith(":"):
        return parse_integer(line)

    raise InvalidMessageError

def deserialise(msg: str) -> str | int:
    if not msg.endswith(CRLF):
        raise InvalidMessageError

    lines = msg.rstrip(CRLF).split(CRLF)
    return parse(lines)
