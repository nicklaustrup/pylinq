# filepath: /c:/Users/nlaus/randomcode/linq/server.py
import asyncio
import websockets
import json

clients = set()


async def handler(websocket):
    # Register client
    clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            data = json.loads(message)
            # Relay message to other clients
            for client in clients:
                if client != websocket:
                    print(f"Sending message to client: {data}")
                    await client.send(json.dumps(data))
    finally:
        # Unregister client
        clients.remove(websocket)


async def main():
    async with websockets.serve(handler, "localhost", 9999):
        print("Starting server...")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
