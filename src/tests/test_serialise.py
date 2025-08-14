import pytest

from src.whodis.serialise import SerialiseResult, serialise


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
