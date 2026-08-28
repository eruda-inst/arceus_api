import asyncio
import json

import websockets


async def main():
    async with websockets.connect(uri="ws://localhost:8000/api/v1/logs/") as ws:
        await ws.send(json.dumps({"nome_cliente": "gabriel"}))
        res = await ws.recv()
        print(res)


if __name__ == "__main__":
    asyncio.run(main())
