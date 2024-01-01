from typing import Any, Optional

# TODO: need to return partnet and name
def fetch_attr(module: Any, name: str) -> tuple[Optional[Any], Any, str]:
    """Returns None when member cannot be found in `module`"""
    name_chunks = name.split(".")
    curr_name = ""
    curr_module = module
    target = None

    while len(name_chunks) > 0:
        # drill down for member in name path
        curr_name = name_chunks.pop(0)

        if curr_name in curr_module.__dict__:
            member = curr_module.__dict__[curr_name]
        else:
            # TODO: handle?
            break

        if len(name_chunks) > 0:
            curr_module = member
        else:
            target = member

    return (target, curr_module, curr_name)


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
    (original, parent, member_name) = fetch_attr(module, name)
    if original and callable(original):
        wrapped = factory(original, **kwargs)
        setattr(parent, member_name, wrapped)
    else:
        raise AttributeError(f"No attr found for {name} in {module}")
