from dataclasses import dataclass

from src.whodis.shared import CRLF, InvalidMessageError, RESPDataType


@dataclass(frozen=True)
class ParseResult:
    data: RESPDataType
    bytes_consumed: int


def deserialise(msg: str) -> ParseResult:
    if not msg.endswith(CRLF):
        error = "Message could not be parsed: missing CRLF terminator"
        raise InvalidMessageError(error)

    result = _parse(msg)
    # As each _parse_* function must be stream-friendly, they cannot detect if
    # there are trailing bytes (as arrays and bulk strings will contain CRLFs)
    if result.bytes_consumed != len(msg):
        error = "Message could not be parsed: trailing data after message"
        raise InvalidMessageError(error)

    return result


def _parse(msg: str) -> ParseResult:
    match msg[0]:
        case "*":
            return _parse_array(msg)
        case "$":
            return _parse_bulk_string(msg)
        case "+":
            return _parse_simple_string(msg)
        case ":":
            return _parse_integer(msg)
        case _:
            error = "Message could not be parsed: unsupported data type"
            raise InvalidMessageError(error)


def _parse_array(msg: str) -> ParseResult:
    if not msg.startswith("*") or not msg.endswith(CRLF):
        error = "Message could not be parsed as an array"
        raise InvalidMessageError(error)

    try:
        prefix_end = msg.index(CRLF)
        num_elements = int(msg[1:prefix_end])
    except (ValueError, IndexError) as e:
        error = "Number of elements could not be determined for array"
        raise InvalidMessageError(error) from e

    bytes_consumed = prefix_end + len(CRLF)
    array_elements: list[RESPDataType] = []

    for _ in range(num_elements):
        # Preferred to catching an IndexError if loop overruns
        if bytes_consumed >= len(msg):
            error = "Array has fewer elements than declared"
            raise InvalidMessageError(error)

        parse_result = _parse(msg[bytes_consumed:])
        array_elements.append(parse_result.data)
        bytes_consumed += parse_result.bytes_consumed

    if bytes_consumed != len(msg):
        error = "Message length does not match content for array"
        raise InvalidMessageError(error)

    return ParseResult(
        data=array_elements,
        bytes_consumed=bytes_consumed,
    )


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
    if len(msg) < bytes_consumed or msg[end:bytes_consumed] != CRLF:
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

    value = msg[1:end]
    if "\r" in value or "\n" in value:
        error = "Content contains newline characters"
        raise InvalidMessageError(error)

    bytes_consumed = end + len(CRLF)

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

    try:
        value = int(msg[1:end])
    except ValueError as e:
        error = "Could not parse: not an integer"
        raise InvalidMessageError(error) from e

    bytes_consumed = end + len(CRLF)

    return ParseResult(
        data=value,
        bytes_consumed=bytes_consumed,
    )
