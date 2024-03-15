from setuptools import setup, Extension
import toml

NAME = "eave-tracing-python"
VERSION = "0.1.0"

if __name__ == "__main__":
    with open("pyproject.toml") as meta:
        pyproject = toml.loads(meta.read())["project"]

    version = pyproject["version"]

    setup(
        version=VERSION,
        py_modules=[NAME],
        ext_modules=[
            Extension(
                "functiontracing",
                ["python/functiontracing.c", "mpack/mpack.c"],
                extra_compile_args=["-std=c11", "-O2"],
                define_macros=[("PACKAGE_VERSION", '"{}"'.format(version))],
            )
        ],
    )
