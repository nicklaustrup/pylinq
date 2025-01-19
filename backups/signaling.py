import json
import asyncio
import websockets


class SignalingServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def handle_messages(self, websocket):
        try:
            async for message in websocket:
                # Parse the signaling message
                data = json.loads(message)

                # Check the type of the message (e.g., offer, answer, candidate)
                if data['type'] == 'offer':
                    # Broadcast offer to the other peer
                    await self.broadcast(websocket, data)
                elif data['type'] == 'answer':
                    # Broadcast answer to the initiating peer
                    await self.broadcast(websocket, data)
                elif data['type'] == 'candidate':
                    # Broadcast ICE candidate to the other peer
                    await self.broadcast(websocket, data)

        except Exception as e:
            print(f"Error handling message: {e}")
        finally:
            await self.unregister(websocket)

    async def broadcast(self, websocket, message):
        # Broadcast the message to all connected peers except the sender
        for client in self.clients:
            if client != websocket:
                try:
                    await client.send(json.dumps(message))
                except:
                    await self.unregister(client)

    async def main(self):
        async with websockets.serve(self.handler, self.host, self.port):
            print(f"Signaling server started on {self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            await self.handle_messages(websocket)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            await self.unregister(websocket)


if __name__ == '__main__':
    server = SignalingServer()
    asyncio.run(server.main())
