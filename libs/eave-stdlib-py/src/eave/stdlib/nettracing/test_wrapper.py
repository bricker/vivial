from eave.stdlib.nettracing.util import wrap
from eave.stdlib.nettracing.py_agent import _replace_import

math_wrap_count = 0
dummy_wrap_count = 0

def test_single_level_import_wrap():
    def mysqrt_factory(wrapped, **kwargs):
        def mysqrt(*args, **kwargs):
            global math_wrap_count
            # print(f"we wrapping {args}, {kwargs}")
            res = wrapped(*args, **kwargs)
            math_wrap_count += 1
            return res
        return mysqrt

    def mysqrt_wrapper(module):
        wrap(module, "sqrt", mysqrt_factory)

    _replace_import("math", mysqrt_wrapper)

    import math
    assert math_wrap_count == 0, "Wrong initial test state"
    math.sqrt(16) # should wrap
    assert math_wrap_count == 1, "Unexpected number of function calls made/wrapped"
    math.log2(34) # shouldnt wrap
    assert math_wrap_count == 1, "math.log2 should not be wrapped"

def test_multi_level_import_wrap():
    def my_dummy_factory(wrapped, **kwargs):
        def my_dummy(*args, **kwargs):
            global dummy_wrap_count
            res = wrapped(*args, **kwargs)
            dummy_wrap_count += 1
            return res
        return my_dummy

    def my_dummy_wrapper(module):
        wrap(module, "Target.one", my_dummy_factory)

    _replace_import("eave.stdlib.nettracing.test_helpers.dummy_target", my_dummy_wrapper)

    from eave.stdlib.nettracing.test_helpers.dummy_target import Target
    assert dummy_wrap_count == 0, "Wrong initial test state"
    t = Target()
    t.one()
    assert dummy_wrap_count == 1, "Unexpected number of function calls made/wrapped"
    t.two()
    assert dummy_wrap_count == 1, "Other member functions should not be wrapped"


test_single_level_import_wrap()
test_multi_level_import_wrap()
print("TESTS PASSED")