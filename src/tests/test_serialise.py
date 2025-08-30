import pytest

from src.whodis.serialise import Kind, SerialiseError, SerialiseResult, serialise


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({"a": 1}, id="protocol_unsupported_data_type"),
    ],
)
def test_invalid_protocol_messages(data: str) -> None:
    with pytest.raises(SerialiseError):
        serialise(data)


@pytest.mark.parametrize(
    ("data", "expected_serialise_result"),
    [
        pytest.param("OK", SerialiseResult("+OK\r\n", 5), id="simple_content"),
        pytest.param("hello world ", SerialiseResult("+hello world \r\n", 15), id="simple_trailing_space"),
        pytest.param(" hello world", SerialiseResult("+ hello world\r\n", 15), id="simple_leading_space"),
        pytest.param(" ", SerialiseResult("+ \r\n", 4), id="simple_one_space"),
        pytest.param("   ", SerialiseResult("+   \r\n", 6), id="simple_three_spaces"),
    ],
)
def test_valid_simple_strings(data: str, expected_serialise_result: str) -> None:
    serialise_result = serialise(data, kind=Kind.PROTOCOL)
    assert serialise_result == expected_serialise_result


@pytest.mark.parametrize(
    ("data", "expected_serialise_result"),
    [
        pytest.param("ERR", SerialiseResult("-ERR\r\n", 6), id="error_content"),
        pytest.param("hello world ", SerialiseResult("-hello world \r\n", 15), id="error_trailing_space"),
        pytest.param(" hello world", SerialiseResult("- hello world\r\n", 15), id="error_leading_space"),
        pytest.param(" ", SerialiseResult("- \r\n", 4), id="error_one_space"),
        pytest.param("   ", SerialiseResult("-   \r\n", 6), id="error_three_spaces"),
    ],
)
def test_valid_errors(data: str, expected_serialise_result: str) -> None:
    serialise_result = serialise(data, kind=Kind.ERROR)
    assert serialise_result == expected_serialise_result


@pytest.mark.parametrize(
    ("data", "expected_serialise_result"),
    [
        pytest.param(123, SerialiseResult(":123\r\n", 6), id="integer_content"),
        pytest.param(2**63, SerialiseResult(":9223372036854775808\r\n", 22), id="integer_large"),
    ],
)
def test_valid_integers(data: str, expected_serialise_result: str) -> None:
    serialise_result = serialise(data)
    assert serialise_result == expected_serialise_result


@pytest.mark.parametrize(
    ("data", "expected_serialise_result"),
    [
        pytest.param("", SerialiseResult("$0\r\n\r\n", 6), id="bulk_empty"),
        pytest.param("bulkstring", SerialiseResult("$10\r\nbulkstring\r\n", 17), id="bulk_content"),
        pytest.param("bulk\r\nstring", SerialiseResult("$12\r\nbulk\r\nstring\r\n", 19), id="embedded_crlf"),
    ],
)
def test_valid_bulk_strings(data: str, expected_serialise_result: str) -> None:
    serialise_result = serialise(data)
    assert serialise_result == expected_serialise_result


@pytest.mark.parametrize(
    ("data", "kind", "expected_serialise_result"),
    [
        pytest.param(["hi"], Kind.PROTOCOL, SerialiseResult("*1\r\n+hi\r\n", 9), id="array_content_protocol"),
        pytest.param(
            ["a", "b"],
            Kind.PROTOCOL,
            SerialiseResult("*2\r\n+a\r\n+b\r\n", 12),
            id="array_multiple_elements_protocol",
        ),
        pytest.param(
            ["hi"],
            Kind.NON_PROTOCOL,
            SerialiseResult("*1\r\n$2\r\nhi\r\n", 12),
            id="array_content_non_protocol",
        ),
        pytest.param(
            ["echo", "hello world"],
            Kind.NON_PROTOCOL,
            SerialiseResult("*2\r\n$4\r\necho\r\n$11\r\nhello world\r\n", 32),
            id="array_multiple_elements_non_protocol",
        ),
        pytest.param(
            [1, "a"],
            Kind.NON_PROTOCOL,
            SerialiseResult("*2\r\n:1\r\n$1\r\na\r\n", 15),
            id="array_integer_bulk",
        ),
        pytest.param(
            ["first", ["nested1", "nested2"]],
            Kind.NON_PROTOCOL,
            SerialiseResult("*2\r\n$5\r\nfirst\r\n*2\r\n$7\r\nnested1\r\n$7\r\nnested2\r\n", 45),
            id="array_nested",
        ),
    ],
)
def test_valid_arrays(data: str, kind: Kind, expected_serialise_result: str) -> None:
    serialise_result = serialise(data, kind)
    assert serialise_result == expected_serialise_result
