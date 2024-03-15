from setuptools import setup, Extension

PACKAGE_NAME = "eave-tracing-python"
PACKAGE_VERSION = "0.1.0"

if __name__ == "__main__":
    setup(
        ext_modules=[
            Extension(
                "_functiontrace",
                ["src/eave/tracing/python/_functiontrace.c", "src/eave/tracing/python/mpack/mpack.c"],
                extra_compile_args=["-std=c11", "-O2"],
                define_macros=[("PACKAGE_VERSION", '"{}"'.format(PACKAGE_VERSION))],
            )
        ],
    )
