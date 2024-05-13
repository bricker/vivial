from typing import Any
import uvicorn.workers

class EaveUvicornWorker(uvicorn.workers.UvicornWorker):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config.server_header = False
