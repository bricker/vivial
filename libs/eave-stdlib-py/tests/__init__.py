import eave.stdlib.requests
import eave.stdlib.eave_origins

# set a core_api client origin to make tests not crash from it being unset
eave.stdlib.requests.set_origin(eave.stdlib.eave_origins.EaveOrigin.eave_slack_app)
