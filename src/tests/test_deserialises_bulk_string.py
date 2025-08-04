import pytest

from src.whodis.deserialise import InvalidMessageError, deserialise


def test_deserialises_bulk_string() -> None:
    sent_message = "$10\r\nbulkstring\r\n"
    expected_message = "bulkstring"

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_deserialises_crlf_only() -> None:
    sent_message = "$0\r\n\r\n"
    expected_message = ""

    deserialised_message = deserialise(sent_message)

    assert deserialised_message == expected_message

def test_raises_exception_for_missing_crlf() -> None:
    sent_message = "$10\r\nbulkstring"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_embedded_crlf_with_correct_length() -> None:
    sent_message = "$12\r\nbulk\r\nstring\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_multiline_input() -> None:
    sent_message = "$10\r\none\r\ntwo\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_when_content_length_incorrect() -> None:
    sent_message = "$9\r\nbulkstring\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_when_content_length_zero_with_content() -> None:
    sent_message = "$0\r\na\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_multiline_input_with_content_length() -> None:
    sent_message = "$3\r\nabc\r\ncde\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)

def test_raises_exception_for_null_bulk_string() -> None:
    sent_message = "$-1\r\n"

    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)
