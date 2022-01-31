import asyncio
import json
from functools import wraps
from typing import List, Literal
from rich import print, inspect
from time import time


def guard_class_property(prop_name: str):
    def guard_decorator(fn):
        @wraps(fn)
        def guarded_fn(self, *args, **kwargs):
            if (getattr(self, prop_name) is not None):
                return fn(self, *args, **kwargs)

        return guarded_fn

    return guard_decorator


def accepts_cancelation(fn):
    @wraps(fn)
    def guarded_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except asyncio.CancelledError:
            raise

    return guarded_fn


def measure_time(fn):
    @wraps(fn)
    def measured_fn(*args, **kwargs):
        start = time()
        res = fn(*args, **kwargs)
        duration = time() - start 

        print(f"Execution took {duration}")

        return res

    return measured_fn

class RofiBlocks():
    def __init__(self):
        self.rofi_base_cmd = ["rofi"]
        self.proc_queue = asyncio.Queue()

    async def launch(self):
        cmd = self.rofi_base_cmd + ["-modi", "blocks", "-show", "blocks"]
        self.proc = await asyncio.create_subprocess_exec(*cmd,
                                                   stdin=asyncio.subprocess.PIPE,
                                                   stdout=asyncio.subprocess.PIPE)

    @guard_class_property("proc")
    async def _watch_stdout(self):
        while self.proc.returncode is None:
            await asyncio.sleep(0) # THIS IS CRITICAL
            line = await self.proc.stdout.readline()
            line = line.decode().replace("\n", "")

            if (len(line) > 0):
                try:
                    await self.proc_queue.put(json.loads(line))
                except json.decoder.JSONDecodeError:
                    pass

    @staticmethod
    def _write_blocks_content(proc: asyncio.subprocess.Process, content: dict):
        dump = (json.dumps(content) + "\n").encode()

        if proc.returncode is None:
            proc.stdin.write(dump)

    async def interact(self):
        wait_task = asyncio.create_task(self.proc.wait())
        read_task = asyncio.create_task(self._watch_stdout())

        while True:
            feed_task = asyncio.create_task(self.proc_queue.get())

            done, pending = await asyncio.wait([wait_task, feed_task],
                                               return_when="FIRST_COMPLETED")

            if (feed_task in done):
                yield feed_task.result()

            if (wait_task in done):
                # Clean tasks
                for pending_task in pending:
                    pending_task.cancel()

                read_task.cancel()

                self.proc = None

                return

    @guard_class_property("proc")
    def update(self, *, msg: str = None, overlay: str = None,
                    prompt: str = None, input: str = None,
                    input_action: Literal["filter", "send"] = None, 
                    active_entry: int = None,
                    lines: List[str] = None):

        update_dict = {
            "message": msg,
            "overlay": overlay,
            "prompt": prompt,
            "input": input,
            "input action": input_action,
            "active_entry": active_entry,
            "lines": lines
        }

        update_dict = {k: v for k, v in update_dict.items() if v is not None}

        self._write_blocks_content(self.proc, update_dict)

