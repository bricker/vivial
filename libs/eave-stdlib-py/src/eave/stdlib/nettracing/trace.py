import time
# NOTE: scapy is GPL2, which could be a problem
from scapy.all import *

# TODO: get some more useful packet body info out of the lambda
t = AsyncSniffer(prn=lambda x: x.summary(), store=False, filter="tcp")

t.start()

time.sleep(10)

t.stop()
