import multiprocessing
import multiprocessing.connection
import os
import signal
import sys
from multiprocessing.connection import Connection, Listener
from queue import Empty
from types import FrameType
from typing import Any, cast

_sockaddr = "/tmp/eaveagent.sock"  # noqa: S108
_endmsg = "EOF"

_buffer_maxsize = 1000


def _flush(buffer: list[Any]) -> None:
    print("Flushing queue, size:", len(buffer))
    _buffer_copy = buffer.copy()

    try:
        # TODO: Send data to Eave API
        pass
    except Exception as e:
        print(e)
    else:
        buffer.clear()
        print("Done")


def _q_processor(q: multiprocessing.Queue) -> None:
    running = True

    def _sighandler(signum: int, frame: FrameType | None) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _sighandler)

    buffer: list[Any] = []

    while True:
        try:
            msg = q.get(timeout=1)
            buffer.append(msg)

            if len(buffer) >= _buffer_maxsize:
                _flush(buffer)

        except Empty:
            # This allows the queue to be flushed before exiting this process
            if not running:
                _flush(buffer)
                break


def _connection_handler(conn: Connection) -> None:
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_q_processor, args=(q,))
    p.start()

    def _cleanup() -> None:
        conn.close()
        p.terminate()
        p.join(timeout=30)

    def _sighandler(signum: int, frame: FrameType | None) -> None:
        _cleanup()
        sys.exit(signum)

    signal.signal(signal.SIGTERM, _sighandler)

    while msg := conn.recv():
        if msg == _endmsg:
            _cleanup()
            break

        q.put(msg, block=False)


def start_controller() -> None:
    running = True
    listener = Listener(address=_sockaddr, family="AF_UNIX")

    # FIXME: Using private properties to set a timeout on socket operations.
    # This allows `listener.accept()` to be effectively non-blocking.
    listener._listener._socket.settimeout(1)  # type: ignore  # noqa: SLF001
    workers: list[multiprocessing.Process] = []

    print("Eave agent started. (Ctrl-C to stop)", os.getpid())

    def _cleanup() -> None:
        for worker in workers:
            worker.terminate()

        sentinels = [w.sentinel for w in workers]
        while sentinels:
            for sentinel in multiprocessing.connection.wait(sentinels, timeout=60):
                sentinels.remove(cast(int, sentinel))

    def _sighandler(signum: int, frame: FrameType | None) -> None:
        print("Shutting down...", os.getpid())
        nonlocal running
        running = False
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    signal.signal(signal.SIGTERM, _sighandler)
    signal.signal(signal.SIGINT, _sighandler)

    print("Waiting for connections...")

    try:
        while True:
            if not running:
                break
            for worker in workers:
                if not worker.is_alive():
                    worker.terminate()  # Actively cleanup defunct processes
                    workers.remove(worker)

            try:
                conn = listener.accept()
                print("Connection accepted")
                p = multiprocessing.Process(target=_connection_handler, args=(conn,))
                p.start()
                workers.append(p)
                conn.close()
            except TimeoutError:
                continue
    finally:
        _cleanup()


# if __name__ == "__main__":
#     start_controller()
