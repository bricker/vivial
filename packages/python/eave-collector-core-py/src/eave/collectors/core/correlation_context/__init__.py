from .async_task import AsyncioCorrelationContext
from .thread import ThreadedCorrelationContext

# TODO: figure out which ctx storage type we need at runtime?
corr_ctx = ThreadedCorrelationContext()
