import pytest

from src.whodis.deserialise import InvalidMessageError, deserialise


def test_deserialises_simple_string() -> None:
    sent_message = "+hello world\r\n"
    expected_message = "hello world"

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_deserialises_simple_string_ending_with_space() -> None:
    sent_message = "+hello world \r\n"
    expected_message = "hello world "

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_deserialises_simple_string_starting_with_space() -> None:
    sent_message = "+ hello world\r\n"
    expected_message = " hello world"

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_deserialises_simple_string_with_one_space() -> None:
    sent_message = "+ \r\n"
    expected_message = " "

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_deserialises_simple_string_with_only_spaces() -> None:
    sent_message = "+   \r\n"
    expected_message = "   "

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_raises_exception_for_empty_message() -> None:
    sent_message = ""

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_no_data() -> None:
    sent_message = "+\r\n"

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
    sent_message = "*hello world\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_multiline_input() -> None:
    sent_message = "+hello world\r\nline two\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)
