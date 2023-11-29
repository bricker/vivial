from dataclasses import dataclass
import sys
from types import FrameType
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from _typeshed import TraceFunction

def tracefunc(fname: FrameType, event: str, arg: Any) -> Optional["TraceFunction"]:
    fargs = fname.f_code.co_varnames[:fname.f_code.co_argcount]
    kwargs = fname.f_code.co_varnames[:fname.f_code.co_kwonlyargcount]
    posargs = fname.f_code.co_varnames[:fname.f_code.co_kwonlyargcount]

    print(
        "[TRACE]",
        "\n\t>", event, fname.f_code.co_name,
        "\n\t>> fname.f_code.co_argcount=", fname.f_code.co_argcount,
        "\n\t>> fname.f_code.co_kwonlyargcount=", fname.f_code.co_kwonlyargcount,
        "\n\t>> fname.f_code.co_posonlyargcount=", fname.f_code.co_posonlyargcount,
        "\n\t>> fname.f_code.co_varnames=", fname.f_code.co_varnames,
        "\n\t>> fargs=", fargs,
        "\n\t>> kwargs=", kwargs,
        "\n\t>> posargs=", posargs,
        "\n\t>> f_locals=", fname.f_locals, # FIXME: f_locals doesn't work with dataclasses?

        # "\n\t> fname.f_code.co_lnotab=", fname.f_code.co_lnotab,
        # "\n\t> fname.f_code.co_flags=", fname.f_code.co_flags,
        # "\n\t> fname.f_code.co_linetable=", fname.f_code.co_linetable,
        # "\n\t> fname.f_code.co_argcount=", fname.f_code.co_argcount,
        # "\n\t> fname.f_code.co_lines=", next(iter(fname.f_code.co_lines())),
        # "\n\t> fname.f_code.co_names=", fname.f_code.co_names,
        # "\n\t> fname.f_code.co_positions=", next(iter(fname.f_code.co_positions())),
        "\n\t>> arg=", arg,
    )
    return tracefunc

sys.settrace(tracefunc)

class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

def print_name(*, person: Person, newline: bool = True) -> None:
    name = person.name
    print(name)

def print_age(*, person: Person, newline: bool = True) -> None:
    age = person.age
    print(age)

def print_person_info(person: Person) -> None:
    print_name(person=person)
    print_age(person=person)

person = Person(name="Bryan", age=35)
print_person_info(person)