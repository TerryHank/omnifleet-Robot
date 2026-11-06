"""Lossless WebSocket compression for display traffic; forward ROS payloads unchanged."""
import asyncio
import websockets
from websockets.extensions.permessage_deflate import ServerPerMessageDeflateFactory


async def forward(source, destination):
    async for message in source:
        await destination.send(message)


async def proxy(client, _path):
    try:
        async with websockets.connect('ws://127.0.0.1:8765',
                                      subprotocols=[client.subprotocol], compression=None,
                                      max_size=32*1024*1024, max_queue=1) as upstream:
            tasks = [asyncio.create_task(forward(client, upstream)),
                     asyncio.create_task(forward(upstream, client))]
            _, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    except (OSError, websockets.WebSocketException):
        await client.close(code=1011, reason='Foxglove bridge unavailable')


async def serve():
    compression = ServerPerMessageDeflateFactory(server_no_context_takeover=True,
                                                 client_no_context_takeover=True,
                                                 compress_settings={'level': 1})
    async with websockets.serve(proxy, '0.0.0.0', 8766, compression=None,
                                extensions=[compression],
                                subprotocols=['foxglove.sdk.v1', 'foxglove.websocket.v1'],
                                max_size=32*1024*1024, max_queue=1):
        print('Display bridge ws://0.0.0.0:8766 -> :8765; permessage-deflate level 1', flush=True)
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(serve())
