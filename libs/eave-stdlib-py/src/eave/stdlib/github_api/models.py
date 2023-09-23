from typing import Optional
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

# Source response object defined in Github API
# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class GithubRepository(BaseResponseModel):
    node_id: str
    full_name: str


class FileChange(BaseResponseModel):
    path: str
    """path from github repo root to file to change"""
    contents: str
    """base64 encoded string to replace the content of the file at `path`"""

class GithubRepoInput(BaseInputModel):
    """
    For sending the repo ID to the Eave Github App API when performing operations on a repository
    """

    external_repo_id: str

class ExternalGithubRepoOwner(BaseResponseModel):
    id: Optional[str]
    login: Optional[str]
    avatar_url: Optional[str]

class ExternalGithubRepo(BaseResponseModel):
    id: Optional[str]
    name: Optional[str]
    url: Optional[str]
    description: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    pushed_at: Optional[str]
    owner: Optional[ExternalGithubRepoOwner]
