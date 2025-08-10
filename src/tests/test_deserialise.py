import pytest

from src.whodis.deserialise import InvalidMessageError, ParseResult, deserialise


@pytest.mark.parametrize(
    "sent_message",
    [
        pytest.param("", id="protocol_empty"),
        pytest.param("+hello world", id="protocol_missing_crlf"),
        pytest.param("\r\nhello world\r\n", id="protocol_missing_prefix"),
        pytest.param("&hello world\r\n", id="protocol_unsupported_prefix"),
    ],
)
def test_invalid_protocol_messages(sent_message: str) -> None:
    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)


@pytest.mark.parametrize(
    ("sent_message", "expected_message"),
    [
        pytest.param("$10\r\nbulkstring\r\n", "bulkstring", id="bulk_content"),
        pytest.param("$0\r\n\r\n", "", id="bulk_empty"),
    ],
)
def test_valid_bulk_strings(sent_message: str, expected_message: str) -> None:
    deserialised_message = deserialise(sent_message)
    assert deserialised_message == expected_message


@pytest.mark.parametrize(
    "sent_message",
    [
        pytest.param("$12\r\nbulk\r\nstring\r\n", id="bulk_embedded_crlf"),
        pytest.param("$10\r\none\r\ntwo\r\n", id="bulk_multiline_body"),
        pytest.param("$9\r\nbulkstring\r\n", id="bulk_incorrect_length"),
        pytest.param("$0\r\na\r\n", id="bulk_zero_length_with_content"),
        pytest.param("$3\r\nabc\r\ncde\r\n", id="bulk_extra_line_after_body"),
        pytest.param("$-1\r\n", id="bulk_null"),
    ],
)
def test_invalid_bulk_strings(sent_message: str) -> None:
    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)


@pytest.mark.parametrize(
    ("sent_message", "expected_message"),
    [
        pytest.param("+hello world\r\n", ParseResult("hello world", 14), id="simple_content"),
        pytest.param("+hello world \r\n", ParseResult("hello world ", 15), id="simple_trailing_space"),
        pytest.param("+ hello world\r\n", ParseResult(" hello world", 15), id="simple_leading_space"),
        pytest.param("+ \r\n", ParseResult(" ", 4), id="simple_one_space"),
        pytest.param("+   \r\n", ParseResult("   ", 6), id="simple_three_spaces"),
    ],
)
def test_valid_simple_strings(sent_message: str, expected_message: str) -> None:
    deserialised_message = deserialise(sent_message)
    assert deserialised_message == expected_message


@pytest.mark.parametrize(
    "sent_message",
    [
        pytest.param("+\r\n", id="simple_no_content"),
        pytest.param("+hello world\r\nline two\r\n", id="simple_extra_line_after_body"),
    ],
)
def test_invalid_simple_strings(sent_message: str) -> None:
    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)


@pytest.mark.parametrize(
    ("sent_message", "expected_result"),
    [
        pytest.param(":123\r\n", ParseResult(123, 6), id="integer_content"),
        pytest.param(f":{2**63!s}\r\n", ParseResult(2**63, len(str(2**63))+3), id="integer_large"),
    ],
)
def test_valid_integers(sent_message: str, expected_result: ParseResult) -> None:
    parse_result = deserialise(sent_message)
    assert parse_result == expected_result


@pytest.mark.parametrize(
    "sent_message",
    [
        pytest.param(":abc\r\n", id="integer_nonnumeric"),
        pytest.param(":\r\n", id="integer_no_content"),
        pytest.param(":123\r\n456\r\n", id="integer_embedded_crlf"),
        pytest.param(":123.456\r\n", id="integer_float"),
    ],
)
def test_invalid_integers(sent_message: str) -> None:
    with pytest.raises(InvalidMessageError):
        deserialise(sent_message)
