from setuptools import Extension, setup

setup(
    ext_modules=[Extension("eave.stdlib.ctracing", ["src/eave/stdlib/ctracing/ctracingmodule.c"])],
)
