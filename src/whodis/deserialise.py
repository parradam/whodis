# Defines carriage return/line feed, used as a terminator and a delimiter
CRLF = "\r\n"

class InvalidMessageError(ValueError):
    pass

def deserialise(msg: str) -> str | int:
    if not msg.endswith(CRLF):
        error = "Message could not be parsed: missing CRLF terminator"
        raise InvalidMessageError(error)
    return _parse(msg)

def _parse(msg: str) -> str | int:
    match msg[0]:
        case "$":
            return _parse_bulk_string(msg)
        case "+":
            return _parse_simple_string(msg)
        case ":":
            return _parse_integer(msg)
        case _:
            error = "Message could not be parsed: unsupported data type"
            raise InvalidMessageError(error)

def _parse_bulk_string(msg: str) -> str:
    if not msg.startswith("$") or not msg.endswith(CRLF):
        error = "Message could not be parsed as a bulk string"
        raise InvalidMessageError(error)

    try:
        prefix_end = msg.index(CRLF)
        num_chars = int(msg[1:prefix_end])
    except (ValueError, IndexError) as e:
        error = "Content length could not be determined for bulk string"
        raise InvalidMessageError(error) from e

    # Don't allow null bulk strings; this isn't RESP3, we're better than that
    if num_chars < 0:
        error = "Content length is negative"
        raise InvalidMessageError(error)

    content_start = prefix_end + len(CRLF)
    content_end = content_start + num_chars

    if len(msg) != content_end + len(CRLF):
        error = "Content length does not match number of bytes"
        raise InvalidMessageError(error)

    if CRLF in msg[content_start:content_end]:
        error = "Content contains newline characters"
        raise InvalidMessageError(error)

    return msg[content_start:content_end]

def _parse_simple_string(msg: str) -> str:
    if not msg.startswith("+") or not msg.endswith(CRLF):
        error = "Message could not be parsed as a simple string"
        raise InvalidMessageError(error)

    extracted = msg.removeprefix("+").removesuffix(CRLF)
    if len(extracted) == 0:
        error = "Content length is zero"
        raise InvalidMessageError(error)

    if CRLF in extracted:
        error = "Content contains newline characters"
        raise InvalidMessageError(error)

    return extracted

def _parse_integer(msg: str) -> int:
    if not msg.startswith(":") or not msg.endswith(CRLF):
        error = "Message could not be parsed as an integer"
        raise InvalidMessageError(error)

    extracted = msg.removeprefix(":").removesuffix(CRLF)
    if len(extracted) == 0:
        error = "Content length is zero"
        raise InvalidMessageError(error)

    try:
        return int(extracted)
    except ValueError as e:
        error = "Could not parse: not an integer"
        raise InvalidMessageError(error) from e
