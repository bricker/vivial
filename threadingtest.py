import asyncio
import contextvars

v = contextvars.ContextVar("request", default="default")

async def funcA(task: str):
    t=asyncio.current_task()
    assert t

    c = contextvars.copy_context()
    r=c.get(v)

    print(task, "funcA", "t=", t.get_name(), "r=", r)

async def threadMain(task: str):
    # t = threading.current_thread()
    t=asyncio.current_task()
    assert t

    print(f"{task}-0", "thrdM", "t=", t.get_name())

    if task != "task3":
        v.set(f"{task}-request")

    asyncio.create_task(funcA(f"{task}-1"))
    asyncio.create_task(funcA(f"{task}-2"))

def main():
    asyncio.run(threadMain("task1"))
    asyncio.run(threadMain("task2"))
    asyncio.run(threadMain("task3"))

if __name__ == "__main__":
    main()
