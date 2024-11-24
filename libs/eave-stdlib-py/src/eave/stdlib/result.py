class Result[T, E: Exception]:
    ok: bool
    value: T
    exception: E

    def __bool__(self) -> bool:
        return self.ok


class ResultSuccess[T, E: Exception](Result[T, E]):
    ok = True

    def __init__(self, value: T) -> None:
        self.value = value


class ResultFailure[T, E: Exception](Result[T, E]):
    ok = False

    def __init__(self, exception: E) -> None:
        self.exception = exception
