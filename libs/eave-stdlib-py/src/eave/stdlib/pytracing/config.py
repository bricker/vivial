class EaveConfig:
    client_id: str
    client_secret: str
    scope: str | None

    def __init__(self, client_id: str, client_secret: str, scope: str | None = None) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
