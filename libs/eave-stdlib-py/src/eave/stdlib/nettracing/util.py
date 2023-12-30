from typing import Any

# TODO: improve factory typing to use Callable[AnyCallable, kwargs]
def wrap(module: Any, name: str, factory: Any, **kwargs):
    """
    wraps the function/object at `name` from `module` using the `factory`.
    Throws AttributeError if `module` doesnt have any members named `name`

    module - an imported module to replace named target member of (e.g. math)
    name - name of module member to wrap (e.g. "sqrt")
    factory - factory to create a wrapper around the `name` target
    kwargs - any args to pass along to the factory
    """
    if (original := getattr(module, name)) and callable(original):
        wrapped = factory(original, **kwargs)
        setattr(module, name, wrapped)
    else:
        raise AttributeError(f"No attr found for {name} in {module}")
