import json
import os
import uuid

import dotenv
import eave.stdlib.time
import eave.stdlib.util

eave.stdlib.time.set_utc()

dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], ".env.test"), override=True)

os.environ["EAVE_API_BASE_PUBLIC"] = "https://api.eave.tests"
os.environ["EAVE_APPS_BASE_PUBLIC"] = "https://apps.eave.tests"
os.environ["EAVE_WWW_BASE_PUBLIC"] = "https://www.eave.tests"
os.environ["EAVE_COOKIE_DOMAIN"] = ".eave.tests"

os.environ["EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON"] = json.dumps(
    {
        "web": {
            "client_id": str(uuid.uuid4()),
            "project_id": "eavefyi-tests",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": str(uuid.uuid4()),
            "redirect_uris": ["https://api.eave.tests/oauth/google/callback"],
        }
    }
)
