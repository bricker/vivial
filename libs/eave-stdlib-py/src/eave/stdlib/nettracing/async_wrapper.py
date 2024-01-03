# Copyright 2010 New Relic, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any
import textwrap
import functools
import inspect

# intorduced in python 3.5
if hasattr(inspect, 'iscoroutinefunction'):
    def is_coroutine_function(wrapped):
        return inspect.iscoroutinefunction(wrapped)
else:
    def is_coroutine_function(wrapped):
        return False


def is_asyncio_coroutine(wrapped):
    """Return True if func is a decorated coroutine function."""
    return getattr(wrapped, '_is_coroutine', None) is not None


def is_generator_function(wrapped):
    return inspect.isgeneratorfunction(wrapped)



def is_coroutine_callable(wrapped):
    return is_coroutine_function(wrapped) or is_coroutine_function(getattr(wrapped, "__call__", None))

# introduced in python 3.6
if hasattr(inspect, 'isasyncgenfunction'):
    def is_async_generator_function(wrapped):
        return inspect.isasyncgenfunction(wrapped)
else:
    def is_async_generator_function(wrapped):
        return False
    
def evaluate_wrapper(wrapper_string, wrapped):
    values = {
        'wrapper': None, 
        'wrapped': wrapped,
        # 'trace': trace, 
        'functools': functools
    }
    exec(wrapper_string, values)
    return values['wrapper']


def coroutine_wrapper(wrapped):
    WRAPPER = textwrap.dedent("""
    @functools.wraps(wrapped)
    async def wrapper(*args, **kwargs):
        return await wrapped(*args, **kwargs)
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped)
    except Exception:
        return wrapped


def awaitable_generator_wrapper(wrapped):
    WRAPPER = textwrap.dedent("""
    import asyncio

    @functools.wraps(wrapped)
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        result = yield from wrapped(*args, **kwargs)
        return result
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped)
    except:
        return wrapped


def generator_wrapper(wrapped):
    WRAPPER = textwrap.dedent("""
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        result = yield from wrapped(*args, **kwargs)
        return result
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped)
    except:
        return wrapped


def async_generator_wrapper(wrapped):
    WRAPPER = textwrap.dedent("""
    @functools.wraps(wrapped)
    async def wrapper(*args, **kwargs):
        g = wrapped(*args, **kwargs)
        try:
            yielded = await g.asend(None)
            while True:
                try:
                    sent = yield yielded
                except GeneratorExit as e:
                    await g.aclose()
                    raise
                except BaseException as e:
                    yielded = await g.athrow(e)
                else:
                    yielded = await g.asend(sent)
        except StopAsyncIteration:
            return
    """)

    try:
        return evaluate_wrapper(WRAPPER, wrapped)
    except:
        return wrapped


# NOTE: I removed trace param from all these definitions cus dont need it now
# all this string exec seems pretty dumb
def async_wrapper(wrapped) -> Any:
    if is_coroutine_callable(wrapped):
        return coroutine_wrapper
    elif is_async_generator_function(wrapped):
        return async_generator_wrapper
    elif is_generator_function(wrapped):
        if is_asyncio_coroutine(wrapped):
            return awaitable_generator_wrapper
        else:
            return generator_wrapper