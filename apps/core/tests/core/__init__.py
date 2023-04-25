import dotenv

dotenv.load_dotenv()

import eave.core.internal.config
import eave.stdlib.config
import mockito

config_mock = mockito.mock(
    {
        "db_driver": "postgresql+asyncpg",
        "db_host": None,
        "db_port": None,
        "db_user": None,
        "db_pass": None,
        "db_name": "eave-test",
        "eave_api_base": "http://api.eave.localhost",
        "eave_www_base": "http://www.eave.localhost",
        "eave_cookie_domain": ".eave.localhost",
    }
)

eave.core.internal.config.app_config = config_mock
