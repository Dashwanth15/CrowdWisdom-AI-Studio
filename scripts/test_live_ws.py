import asyncio
import websockets
import json

async def test_ws():
    uri = "wss://crowdwisdom-ai-studio-backend.onrender.com/ws/test_client_audit"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri, origin="https://crowdwisdom-ai-studio-ads.onrender.com") as ws:
            print("Connected successfully!")
            msg = await ws.recv()
            print("Received message:", msg)
            await ws.send(json.dumps({"type": "ping"}))
            resp = await ws.recv()
            print("Received ping response:", resp)
    except Exception as e:
        print("WS Error:", type(e), e)

if __name__ == "__main__":
    asyncio.run(test_ws())
