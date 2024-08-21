from eave.collectors.core.agent.data_handler.atoms import AtomHandler
from eave.collectors.core.logging import EAVE_LOGGER

from . import EaveAgent

SHARED_BATCHED_ATOM_WRITE_QUEUE = EaveAgent(logger=EAVE_LOGGER, data_handler=AtomHandler())
