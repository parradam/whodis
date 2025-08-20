# Defines carriage return/line feed, used as a terminator and a delimiter
CRLF = "\r\n"

RESPDataType = int | str | list["RESPDataType"]


class InvalidMessageError(ValueError):
    pass
