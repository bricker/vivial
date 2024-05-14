from .async_task import AsyncioCorrelationContext as AsyncioCorrelationContext
from .thread import ThreadedCorrelationContext as ThreadedCorrelationContext

# TODO: figure out which ctx storage type we need at runtime?
corr_ctx = ThreadedCorrelationContext()
