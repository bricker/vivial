from dotenv import load_dotenv
load_dotenv()

import eave.core.internal.config
import mockito

config_mock = mockito.mock(
    {
        "db_driver": "postgresql+asyncpg",
        "db_host": None,
        "db_port": None,
        "db_user": None,
        "db_pass": None,
        "db_name": "eave-test",
    }
)

eave.core.internal.config.app_config = config_mock
