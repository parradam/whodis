from dataclasses import dataclass
from enum import Enum, auto

from src.whodis.shared import CRLF, RESPDataType


class Kind(Enum):
    PROTOCOL = auto()
    NON_PROTOCOL = auto()

@dataclass(frozen=True)
class SerialiseResult:
    message: str
    bytes_produced: int

class SerialiseError(ValueError):
    pass


def serialise(data: RESPDataType, kind: Kind = Kind.NON_PROTOCOL) -> SerialiseResult:
    if isinstance(data, str) and kind == Kind.PROTOCOL:
        return _serialise_simple_string(data)
    if isinstance(data, str):
        return _serialise_bulk_string(data)
    if isinstance(data, int):
        return _serialise_integer(data)
    error = "Message could not be serialised: unsupported data type"
    raise SerialiseError(error)


def _serialise_simple_string(data: RESPDataType) -> SerialiseResult:
    message = f"+{data}{CRLF}"
    return SerialiseResult(message, len(message))

def _serialise_bulk_string(data: str) -> SerialiseResult:
    message = f"${len(data)}{CRLF}{data}{CRLF}"
    return SerialiseResult(message, len(message))

def _serialise_integer(data: RESPDataType) -> SerialiseResult:
    message = f":{data!s}{CRLF}"
    return SerialiseResult(message, len(message))
