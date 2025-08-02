# Defines carriage return/line feed, used as a terminator and a delimiter
CRLF = "\r\n"

class InvalidMessageError(ValueError):
    pass

def parse_simple_string(line: str) -> str:
    # Cannot accept only one char (the prefix)
    if len(line) == 1:
        raise InvalidMessageError
    return line[1:]

def parse(lines: list[str]) -> str:
    if not lines:
        raise InvalidMessageError

    line = lines[0]
    if line.startswith("+"):
        # Cannot accept more than one line for a simple string
        if len(lines) > 1:
            raise InvalidMessageError
        return parse_simple_string(line)

    raise InvalidMessageError

def deserialise(msg: str) -> str:
    if not msg.endswith(CRLF):
        raise InvalidMessageError

    lines = msg.rstrip(CRLF).split(CRLF)
    return parse(lines)
