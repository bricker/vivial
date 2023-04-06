# from slack_bolt.authorization import AuthorizeResult
import pydantic

# POST
# TODO: return SlackSource network model? see ticket gh comment
async def query(slack_team_id: str) -> EaveAuthorizeResult:
    # TODO: db query
    pass