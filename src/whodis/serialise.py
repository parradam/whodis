from dataclasses import dataclass
from enum import Enum, auto

from src.whodis.shared import CRLF, RESPDataType


class Kind(Enum):
    PROTOCOL = auto()
    NON_PROTOCOL = auto()
    ERROR = auto()


@dataclass(frozen=True)
class SerialiseResult:
    message: str
    bytes_produced: int


class SerialiseError(ValueError):
    pass


def serialise(data: RESPDataType, kind: Kind = Kind.NON_PROTOCOL) -> SerialiseResult:
    if isinstance(data, str):
        if kind == Kind.PROTOCOL:
            return _serialise_simple_string(data)

        if kind == Kind.NON_PROTOCOL:
            return _serialise_bulk_string(data)

        return _serialise_error(data)

    if isinstance(data, list):
        return _serialise_array(data, kind)

    if isinstance(data, int):  # pyright: ignore[reportUnnecessaryIsInstance]
        return _serialise_integer(data)

    error = f"Message could not be serialised: unsupported data {type(data)}"
    raise SerialiseError(error)


def _serialise_simple_string(data: str) -> SerialiseResult:
    message = f"+{data}{CRLF}"
    return SerialiseResult(message, len(message))


def _serialise_bulk_string(data: str) -> SerialiseResult:
    message = f"${len(data)}{CRLF}{data}{CRLF}"
    return SerialiseResult(message, len(message))


def _serialise_error(data: str) -> SerialiseResult:
    message = f"-{data}{CRLF}"
    return SerialiseResult(message, len(message))


def _serialise_array(data: list[RESPDataType], kind: Kind) -> SerialiseResult:
    parts = [f"*{len(data)}{CRLF}"]
    parts.extend(serialise(d, kind).message for d in data)
    message = "".join(parts)
    return SerialiseResult(message, len(message))


def _serialise_integer(data: int) -> SerialiseResult:
    message = f":{data!s}{CRLF}"
    return SerialiseResult(message, len(message))
