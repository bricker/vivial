import enum

class MatchedStrEnum(enum.StrEnum):
    """
    Similar to StrEnum, except enum.auto() returns a string that matches the member name.
    (StrEnum returns the lowercased member name)
    """
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name
