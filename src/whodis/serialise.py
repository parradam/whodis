from dataclasses import dataclass

from src.whodis.shared import CRLF, RESPDataType


@dataclass(frozen=True)
class SerialiseResult:
    message: str
    bytes_produced: int


def serialise(data: RESPDataType) -> SerialiseResult:
    return _serialise_simple_string(data)


def _serialise_simple_string(data: RESPDataType) -> SerialiseResult:
    message = f"+{data}{CRLF}"
    return SerialiseResult(message, len(message))
