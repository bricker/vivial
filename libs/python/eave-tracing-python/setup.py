from setuptools import setup, Extension
import toml


if __name__ == "__main__":
    with open("pyproject.toml") as meta:
        pyproject = toml.loads(meta.read())["project"]

    version = pyproject["version"]

    setup(
        version=version,
        py_modules=[pyproject["name"]],
        ext_modules=[
            Extension(
                "functiontracing",
                ["src/eave/tracing/python/functiontracing.c", "src/eave/tracing/python/mpack/mpack.c"],
                extra_compile_args=["-std=c11", "-O2"],
                define_macros=[("PACKAGE_VERSION", '"{}"'.format(version))],
            )
        ],
    )
