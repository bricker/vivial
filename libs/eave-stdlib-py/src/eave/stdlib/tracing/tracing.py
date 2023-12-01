from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from functools import reduce
import json
import re
import sys
import time
from types import FrameType
from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID, uuid4
import clickhouse_connect

from eave.stdlib.util import compact_deterministic_json

if TYPE_CHECKING:
    from _typeshed import TraceFunction

print(
    "__file__=", __file__,
    "\n__name__=", __name__,
    "\n__package__=", __package__,
)

chclient = clickhouse_connect.get_client(host='localhost')
# chclient.command(cmd="drop table raw_events")

chclient.command(
    cmd=" ".join([
        "create table if not exists raw_events (",
            "team_id UUID,",
            "timestamp DateTime64(6),",
            "event_type LowCardinality(String),",
            "event_params JSON",
        ")",
        "engine MergeTree",
        "primary key (team_id, timestamp)",
    ]),
    settings={
        "allow_experimental_object_type": 1,
    },
)

class EventType(StrEnum):
    functioncall = "functioncall"
    functionreturn = "functionreturn"
    networkin = "networkin"
    networkout = "networkout"

def json_serialize(v: Any) -> Any:
    if hasattr(v, "json_dict"):
        return v.json_dict
    elif hasattr(v, "__dict__"):
        return v.__dict__
    else:
        return v

class EventParams:
    pass

@dataclass
class FunctionCallEventParams(EventParams):
    function_filename: str
    function_lineno: int
    function_name: str
    function_args: dict[str, Any]

@dataclass
class FunctionReturnEventParams(EventParams):
    function_name: str
    function_args: dict[str, str]
    function_return_value: str

@dataclass
class NetworkInEventParams(EventParams):
    request_method: str
    request_path: str
    request_headers: dict[str, str]
    request_payload: str

@dataclass
class NetworkOutEventParams(EventParams):
    request_method: str
    request_url: str
    request_headers: dict[str,str]
    request_payload: str

@dataclass
class RawEvent:
    team_id: UUID
    corr_id: UUID
    timestamp: datetime
    event_type: EventType
    event_params: EventParams

def tracefunc(frame: FrameType, event: str, arg: Any) -> Optional["TraceFunction"]:
    # https://docs.python.org/3/reference/datamodel.html#frame-objects

    if not re.search(r"eave-monorepo/libs", frame.f_code.co_filename):
        return tracefunc

    if not event == "call":
        return tracefunc

    argnames = (
        frame.f_code.co_varnames[:frame.f_code.co_argcount]
        + frame.f_code.co_varnames[:frame.f_code.co_kwonlyargcount]
        + frame.f_code.co_varnames[:frame.f_code.co_kwonlyargcount]
    )

    argvals = {k: v for k, v in frame.f_locals.items() if k in argnames}

    print(
        "[TRACE]",
        "\n\t>", event, frame.f_code.co_name,
        "\n\t>> arg=", arg,
        "\n\t>> fname.f_back=", frame.f_back, # previous frame
        "\n\t>> fname.f_code.co_filename=", frame.f_code.co_filename, # filename of the current event
        "\n\t>> fname.f_lineno=", frame.f_lineno, # line number of the current event
        "\n\t>> fname.f_code.co_firstlineno=", frame.f_code.co_firstlineno, # line number of the first line of the local scope
        "\n\t>> fname.f_code.co_argcount=", frame.f_code.co_argcount, # number of args that have no kw/pos requirement
        "\n\t>> fname.f_code.co_kwonlyargcount=", frame.f_code.co_kwonlyargcount, # number of kw-only args
        "\n\t>> fname.f_code.co_posonlyargcount=", frame.f_code.co_posonlyargcount, # number of pos-only args
        "\n\t>> fname.f_code.co_varnames=", frame.f_code.co_varnames, # names of local variables (includes arg names)
        "\n\t>> f_locals=", frame.f_locals, # dict of local varnames name -> value ... use this to get arg values. FIXME: f_locals doesn't work with dataclasses?
        "\n\t>> argnames=", argnames,
        "\n\t>> argvals=", argvals,

        # "\n\t> fname.f_code.co_lnotab=", fname.f_code.co_lnotab,
        # "\n\t> fname.f_code.co_flags=", fname.f_code.co_flags,
        # "\n\t> fname.f_code.co_linetable=", fname.f_code.co_linetable,
        # "\n\t> fname.f_code.co_argcount=", fname.f_code.co_argcount,
        # "\n\t> fname.f_code.co_lines=", next(iter(fname.f_code.co_lines())),
        # "\n\t> fname.f_code.co_names=", fname.f_code.co_names,
        # "\n\t> fname.f_code.co_positions=", next(iter(fname.f_code.co_positions())),
    )

    team_id=uuid4()
    corr_id=uuid4()
    timestamp=datetime.now()

    if event == "call":
        data = RawEvent(
            team_id=team_id,
            corr_id=corr_id,
            timestamp=timestamp,
            event_type=EventType.functioncall,
            event_params=FunctionCallEventParams(
                function_filename=frame.f_code.co_filename,
                function_lineno=frame.f_code.co_firstlineno,
                function_name=frame.f_code.co_name,
                function_args=argvals,
           ),
        )

        chclient.insert(
            table="raw_events",
            column_names=[
                "team_id",
                "timestamp",
                "event_type",
                "event_params",
            ],
            data=[
                [
                    data.team_id,
                    data.timestamp,
                    data.event_type,
                    json.dumps(data.event_params, indent=None, separators=(",", ":"), default=json_serialize),
                ]
            ],
            settings={
                "async_insert": 1,
                "wait_for_async_insert": 1,
            },
        )

    # elif event == "return":
    #     data = RawEvent(
    #         team_id=team_id,
    #         corr_id=corr_id,
    #         timestamp=timestamp,
    #         event_type=EventType.functionreturn,
    #         event_params=FunctionReturnEventParams(
    #             function_name=fname.f_code.co_name,
    #             function_args=[],
    #             function_return_value=fname.
    #         ),
    #     )


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