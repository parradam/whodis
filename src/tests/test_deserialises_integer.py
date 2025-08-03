import pytest

from src.whodis.deserialise import InvalidMessageError, deserialise


def test_deserialises_integer() -> None:
    sent_message = ":123\r\n"
    expected_message = 123

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_raises_exception_for_nonnumeric_input() -> None:
    sent_message = ":abc\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_no_data() -> None:
    sent_message = ":\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_multiline_input() -> None:
    sent_message = ":123\r\n456\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)
