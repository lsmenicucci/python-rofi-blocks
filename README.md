# Python Rofi blocks 

Async interface for the [amazing interactive modi for rofi](https://github.com/OmarCastro/rofi-blocks). Still in early development and subject to bugs, far from production ready.

```python
import asyncio
from rofi_blocks import RofiBlocks

async def main():
    async with RofiBlocks() as blocks:
        blocks.update(prompt="Google search", input_action="send")

        async for event in blocks.interact():
            # google_results = await handle_event(event)
            blocks.update(lines=google_results)

asyncio.run(main()) 
```

# Usage 

An `RofiBlocks()` instance controls the interaction between the main program and a child process of Rofi with a blocks modi activated. The process is spawned after entering a async context started by a `RofiBlocks()` instance:

```python
blocks = RofiBlocks()
async with blocks:
    # rofi rocks...
  
# or equivalently:

async with RofiBlocks() as blocks:
    # rofi rocks...
```

After that, user input can be consumed by the async generator `blocks.interact()`:

```python
async for event in blocks.interact():
	print(event["name"], event["value"])
```

The events are simply a parsed version of [rofi blocks modi output](https://github.com/OmarCastro/rofi-blocks/tree/c84577749f71f6c0836fc7ca7ec0097d2fe66492#input-format). To update Rofi behavior dynamically, use `blocks.update([option]=value)`:

```python
blocks.update(prompt="Search", msg="Type to begin searching")

blocks.update(prompt="") # Clears prompt

blocks.update(lines=["option 1", "option 2"])
```

Only keyword arguments are acceptable and each one is a mimic of [rofi blocks modi input](https://github.com/OmarCastro/rofi-blocks/tree/c84577749f71f6c0836fc7ca7ec0097d2fe66492#input-format). Passing `None` as value results in an ignored argument.