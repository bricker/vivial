import pydantic


# Source response object defined in Github API
# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class GithubRepository(pydantic.BaseModel):
    node_id: str
    full_name: str


class FileChange(pydantic.BaseModel):
    path: str
    """path from github repo root to file to change"""
    contents: str
    """base64 encoded string to replace the content of the file at `path`"""
