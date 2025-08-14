import pytest

from src.whodis.serialise import SerialiseError, SerialiseResult, serialise


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
    serialise_result = serialise(data)
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
