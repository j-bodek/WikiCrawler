from multiprocessing import pool
import time
from queue import Queue


class TaskQueue:
    """Class used to manage a queue of tasks that are executed by a pool of background threads."""

    def __init__(self, func, interval, processes, **kwargs):
        self._queue = Queue()
        self._pool = pool.ThreadPool(processes=processes)

        for _ in range(processes):
            self._pool.apply_async(
                self._run,
                args=(func, interval),
                kwds=kwargs,
            )

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._pool.close()
        self._pool.join()
        self._pool.terminate()

    def add(self, msg):
        self._queue.put(msg)

    def _run(self, func, interval, **kwargs):
        free = 0
        while free <= 1000:
            msg = None
            if self._queue.qsize() > 0:
                msg = self._queue.get()

            if msg:
                free = 0
                func(msg, **kwargs)
            else:
                free += 1

            time.sleep(interval)
