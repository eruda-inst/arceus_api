import asyncio
import json
from typing import Final

import websockets


async def main():
    token: Final[str] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnYWJyaWVsX2NhdmFsY2FudGVAbmV3bmV0LmNvbS5iciIsInZlciI6MCwiZXhwIjoxNzkwMTcxNzY5fQ.A_pEzFZmm0jE91JcXZ2AO52KDLVhGaDYxBYBwxSameA"
    )
    url: Final[str] = f"ws://localhost:8000/api/v1/logs-ws/?token={token}"

    async with websockets.connect(uri=url) as ws:
        await ws.send(
            json.dumps(
                {
                    "pagina": 2,
                    "itens_por_pagina": 10,
                    "metodo": "GET",
                    "codigo": 200,
                    "endpoint": "contratos",
                }
            )
        )
        async for res in ws:
            print(res)


if __name__ == "__main__":
    asyncio.run(main())
