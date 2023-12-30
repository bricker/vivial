# this file is junk
from eave.stdlib.nettracing.util import wrap
from eave.stdlib.nettracing.py_agent import _replace_import

def mysqrt_factory(wrapped, **kwargs):
    def mysqrt(*args, **kwargs):
        print(f"we wrapping {args}, {kwargs}")
        res = wrapped(*args, **kwargs)
        print("done wrap")
        return res
    return mysqrt

def mysqrt_wrapper(module):
    wrap(module, "sqrt", mysqrt_factory)

_replace_import("math", mysqrt_wrapper)

print("importing math")
import math
print("calling sqrt")
print(math.sqrt(16)) # shoudl wrap
print(math.log2(34)) # shoudlnt wrap