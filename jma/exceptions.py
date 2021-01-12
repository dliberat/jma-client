class JmaException(Exception):
    pass


class NoSessionIdException(JmaException):
    pass


class BadCsvException(JmaException):
    pass
