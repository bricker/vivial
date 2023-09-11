import pydantic

class BaseInputModel(pydantic.BaseModel):
    class Config:
        extra = pydantic.Extra.forbid

# Source response object defined in Github API
# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class GithubRepository(pydantic.BaseModel):
    node_id: str
    full_name: str

class GithubRepoInput(BaseInputModel):
    """
    For sending the repo ID to the Eave Github App API when performing operations on a repository
    """
    external_repo_id: str
