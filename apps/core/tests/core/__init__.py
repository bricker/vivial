import os

import dotenv
import eave.stdlib.time

eave.stdlib.time.set_utc()

dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], ".env.test"), override=True)
