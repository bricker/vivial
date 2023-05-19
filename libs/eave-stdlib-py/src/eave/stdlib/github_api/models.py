import pydantic


# Source response object defined in Github API
# https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
class GithubRepository(pydantic.BaseModel):
    node_id: str
    full_name: str
