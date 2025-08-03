import pytest

from src.whodis.deserialise import InvalidMessageError, deserialise


def test_raises_exception_for_empty_message() -> None:
    sent_message = ""

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_data_after_crlf() -> None:
    sent_message = "+hello world\r\nabc"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_missing_crlf() -> None:
    sent_message = "+hello world"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_missing_prefix() -> None:
    sent_message = "\r\nhello world\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_invalid_prefix() -> None:
    sent_message = "&hello world\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)
