class EaveConfig:
    scope: str | None

    def __init__(self, scope: str | None = None) -> None:
        self.scope = scope
