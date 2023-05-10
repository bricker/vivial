from typing import Optional


class BaseClient:
    async def get_file_content(self, url: str) -> Optional[str]:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()
