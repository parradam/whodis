from dataclasses import dataclass

# Defines carriage return/line feed, used as a terminator and a delimiter
CRLF = "\r\n"


class InvalidMessageError(ValueError):
    pass


@dataclass(frozen=True)
class ParseResult:
    data: int | str
    bytes_consumed: int


def deserialise(msg: str) -> ParseResult | list[int]:
    if not msg.endswith(CRLF):
        error = "Message could not be parsed: missing CRLF terminator"
        raise InvalidMessageError(error)
    return _parse(msg)


def _parse(msg: str) -> ParseResult | list[int]:
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


def _parse_bulk_string(msg: str) -> ParseResult:
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

    start = prefix_end + len(CRLF)
    end = start + num_chars

    bytes_consumed = end + len(CRLF)
    if len(msg) != bytes_consumed:
        error = "Content length does not match number of bytes"
        raise InvalidMessageError(error)

    value = msg[start:end]
    return ParseResult(
        data=value,
        bytes_consumed=bytes_consumed,
    )


def _parse_simple_string(msg: str) -> ParseResult:
    if not msg.startswith("+") or not msg.endswith(CRLF):
        error = "Message could not be parsed as a simple string"
        raise InvalidMessageError(error)

    end = msg.index(CRLF)
    if end == 1:
        error = "Content length is zero"
        raise InvalidMessageError(error)

    bytes_consumed = end + len(CRLF)
    if bytes_consumed != len(msg):
        error = "Content contains newline characters"
        raise InvalidMessageError(error)

    value = msg[1:end]
    return ParseResult(
        data=value,
        bytes_consumed=bytes_consumed,
    )


def _parse_integer(msg: str) -> ParseResult:
    if not msg.startswith(":") or not msg.endswith(CRLF):
        error = "Message could not be parsed as an integer"
        raise InvalidMessageError(error)

    end = msg.index(CRLF)
    if end == 1:
        error = "Content length is zero"
        raise InvalidMessageError(error)

    bytes_consumed = end + len(CRLF)
    if bytes_consumed != len(msg):
        error = "Content contains newline characters"
        raise InvalidMessageError(error)

    try:
        value = int(msg[1:end])
        return ParseResult(
            data=value,
            bytes_consumed=bytes_consumed,
        )
    except ValueError as e:
        error = "Could not parse: not an integer"
        raise InvalidMessageError(error) from e
