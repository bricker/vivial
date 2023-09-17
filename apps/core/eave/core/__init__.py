import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.signing as eave_signing

# All auth tokens coming into the core API should be both signed and issued by the API
EAVE_API_SIGNING_KEY = eave_signing.get_key(eave_origins.EaveApp.eave_api.value)
EAVE_API_JWT_ISSUER = eave_origins.EaveApp.eave_api.value
