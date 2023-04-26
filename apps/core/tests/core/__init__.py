import eave.stdlib.time
import dotenv
import os

eave.stdlib.time.set_utc()

dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], ".env.test"), override=True)