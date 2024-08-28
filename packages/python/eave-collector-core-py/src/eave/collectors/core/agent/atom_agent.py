from eave.collectors.core.agent.data_handler.atoms import AtomHandler
from eave.collectors.core.logging import EAVE_CORE_LOGGER, eave_logger_factory

from . import EaveAgent

SHARED_BATCHED_ATOM_WRITE_QUEUE = EaveAgent(
    logger=eave_logger_factory(f"{EAVE_CORE_LOGGER.name}.shared-atom-write-queue"),
    data_handler=AtomHandler(),
)
