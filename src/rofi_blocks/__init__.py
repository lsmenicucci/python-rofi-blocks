import asyncio
import json
from typing import List, Literal

from .util import guard_class_property

class RofiBlocks():
    def __init__(self):
        self.rofi_base_cmd = ["rofi"]
        self.proc_queue = asyncio.Queue()

    async def __aenter__(self):
        cmd = self.rofi_base_cmd + ["-modi", "blocks", "-show", "blocks"]
        self.proc = await asyncio.create_subprocess_exec(*cmd,
                                                         stdin=asyncio.subprocess.PIPE,
                                                         stdout=asyncio.subprocess.PIPE)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if (self.proc and self.proc.returncode is None):
            self.proc.kill()
        self.proc = None

    @guard_class_property("proc")
    async def _watch_stdout(self):
        while self.proc and self.proc.returncode is None:
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

        if proc and proc.returncode is None:
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

                return

    @guard_class_property("proc")
    def update(self, *, message: str = None, overlay: str = None,
               prompt: str = None, input: str = None,
               input_action: Literal["filter", "send"] = None, 
               active_entry: int = None,
               lines: List[str] = None):

        update_dict = {
            "message": message,
            "overlay": overlay,
            "prompt": prompt,
            "input": input,
            "input action": input_action,
            "active_entry": active_entry,
            "lines": lines
        }

        update_dict = {k: v for k, v in update_dict.items() if v is not None}

        self._write_blocks_content(self.proc, update_dict)

