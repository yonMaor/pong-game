import asyncio

import requests
from fastapi import FastAPI, HTTPException
from threading import Thread

app = FastAPI()

# Server ID (1 or 2) - Set this before running the script
server_id = 2

pong_time_ms = None
is_running = False


def handle_ping_request():
    global pong_time_ms, is_running
    if not is_running:
        raise HTTPException(status_code=409, detail="Game is paused")

    # Respond with pong and update next ping time
    response = {'message': 'pong'}
    if server_id == 1:
        # Simulate sending ping request to server 2 after pong_time_ms
        async def send_ping():
            import time
            await asyncio.sleep(pong_time_ms / 1000)
            response = await requests.get(f'http://localhost:5001/ping')  # Adjust port for server 2
            print(f"Server 1 received: {response.json()}")

        t = Thread(target=send_ping)
        t.start()
    return response


@app.get('/ping')
async def handle_ping():
    return handle_ping_request()


async def start_game(time_ms):
    global pong_time_ms, is_running
    pong_time_ms = time_ms
    is_running = True
    print(f"Server {server_id} started game with pong time {pong_time_ms}ms")

    while is_running:
        # Send ping request to server 2 and wait for pong_time_ms
        import time
        response = await requests.get(f'http://localhost:5002/ping')  # Adjust port for server 2
        print(f"Server {server_id} received: {response.json()}")
        await asyncio.sleep(pong_time_ms / 1000)


def pause_game():
    global is_running
    is_running = False
    print(f"Server {server_id} paused game")


def resume_game():
    global is_running
    if pong_time_ms is None:
        print(f"Server {server_id} can't resume, game not started")
        return
    is_running = True
    print(f"Server {server_id} resumed game")


def stop_game():
    global is_running
    is_running = False
    print(f"Server {sid} stopped game")


# Define functions for CLI to call
@app.get('/start/{time_ms}')
async def start_game_from_cli(time_ms: int):
    start_game(time_ms)
    return {'message': 'Game started'}


@app.get('/pause')
async def pause_game_from_cli():
    pause_game()
    return {'message': 'Game paused'}


@app.get('/resume')
async def resume_game_from_cli():
    resume_game()
    return {'message': 'Game resumed'}


@app.get('/stop')
async def stop_game_from_cli():
    stop_game()
    return {'message': 'Game stopped'}


if __name__ == '__main__':
    # Replace with the port you want the server to run on
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5002)
