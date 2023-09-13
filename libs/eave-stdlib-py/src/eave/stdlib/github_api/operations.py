from typing import Optional
import pydantic
from .models import FileChange


class Endpoint:
    pass


class GetGithubUrlContent(Endpoint):
    class RequestBody(pydantic.BaseModel):
        url: str

    class ResponseBody(pydantic.BaseModel):
        content: Optional[str]


class CreateGithubResourceSubscription(Endpoint):
    class RequestBody(pydantic.BaseModel):
        url: str

class CreateGitHubPullRequest(Endpoint):
    class RequestBody(pydantic.BaseModel):
        repo_name: str
        repo_owner: str
        repo_id: str
        base_branch_name: str
        branch_name: str
        commit_message: str
        pr_title: str
        pr_body: str
        file_changes: list[FileChange]

    class ResponseBody(pydantic.BaseModel):
        pr_number: int