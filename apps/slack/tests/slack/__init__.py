import os
import dotenv
import eave.stdlib.time

eave.stdlib.time.set_utc()
dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], ".env.test"), override=True)

os.environ["EAVE_API_BASE"] = "https://api.eave.tests"
os.environ["EAVE_APPS_BASE"] = "https://apps.eave.tests"
os.environ["EAVE_WWW_BASE"] = "https://www.eave.tests"
os.environ["EAVE_COOKIE_DOMAIN"] = ".eave.tests"
