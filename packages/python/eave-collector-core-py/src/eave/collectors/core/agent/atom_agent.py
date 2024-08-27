from eave.collectors.core.agent.data_handler.atoms import AtomHandler
from eave.collectors.core.logging import eave_logger_factory, EAVE_CORE_LOGGER

from . import EaveAgent

SHARED_BATCHED_ATOM_WRITE_QUEUE = EaveAgent(
    logger=eave_logger_factory(f"{EAVE_CORE_LOGGER.name}.shared-atom-write-queue"),
    data_handler=AtomHandler(),
)
