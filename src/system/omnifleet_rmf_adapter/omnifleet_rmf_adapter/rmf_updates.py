"""Loopback receiver for Humble's official RMF task-state broadcasts."""
import asyncio
import json
import threading
import websockets


class TaskUpdates:
    uri = 'ws://127.0.0.1:8082'

    def __init__(self, inbox):
        self.inbox = inbox
        self.ready = threading.Event()
        self.error = None
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        if not self.ready.wait(3) or self.error:
            raise RuntimeError('RMF state receiver unavailable') from self.error

    async def receive(self, websocket, path):
        async for packet in websocket:
            message = json.loads(packet)
            if message.get('type') == 'task_state_update':
                self.inbox.put(message)

    def run(self):
        async def serve():
            self.loop = asyncio.get_running_loop()
            self.done = self.loop.create_future()
            try:
                async with websockets.serve(self.receive, '127.0.0.1', 8082):
                    self.ready.set()
                    await self.done
            except Exception as error:
                self.error = error
                self.ready.set()
        asyncio.run(serve())

    def close(self):
        self.loop.call_soon_threadsafe(self.done.set_result, None)
        self.thread.join(timeout=3)
