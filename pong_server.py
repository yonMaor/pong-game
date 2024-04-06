from fastapi import FastAPI
from multiprocessing import Process

import uvicorn
import asyncio
import threading
import requests

import CONSTS
import utils



class Server:
    def __init__(self, port: int):
        self.app = None
        self.port = port
        self.is_running = False
        self.listening_thread = None
        self.is_listening = False
        self.pong_time_ms = 0
        self.second_server_port = None
        self.should_ping = False

    def run(self):
        self.app = FastAPI()
        self.define_routes()
        uvicorn.run(self.app, host=CONSTS.HOST, port=self.port)

    async def start_game(self, pong_time_ms: int, second_server_port: int):
        print(f"Server at port {self.port} has entered the game")
        self.pong_time_ms = pong_time_ms
        self.second_server_port = second_server_port
        self.is_listening = True
        self.is_running = True
        self.listening_thread = threading.Thread(target=self.listen)
        self.listening_thread.start()
        return {CONSTS.MESSAGE: CONSTS.GAME_STARTING}

    def listen(self):
        while self.is_running:
            if self.is_listening and self.should_ping:
                print(f"{self.should_ping=}")
                self.send_ping()
                self.should_ping = False

    def send_ping(self):
        print(f"Sending a ping from {self.port} to {self.second_server_port}")
        requests.get(url=utils.build_request_url(server_port=self.second_server_port, endpoint=CONSTS.PING_ENDPOINT),
                     params={"sender_port": self.port, "pong_time_ms": self.pong_time_ms})

    async def handle_ping_request(self, sender_port):
        self.second_server_port = sender_port
        sleep_time = self.pong_time_ms / 1000
        await asyncio.sleep(sleep_time)
        self.should_ping = True
        return {CONSTS.MESSAGE: utils.generate_ping_received_message(self.port, self.second_server_port)}

    def pause_game(self):

        if not self.is_listening:
            return {CONSTS.MESSAGE: "Game isn't currently running"}
        self.is_listening = False
        return {CONSTS.MESSAGE: CONSTS.GAME_PAUSED}

    async def resume_game(self):

        self.is_listening = True
        print("Now listening again")
        return {CONSTS.MESSAGE: CONSTS.GAME_RESUMED}

    async def stop_game(self):

        self.should_ping = False
        self.is_listening = False
        self.is_running = False
        self.listening_thread.join()
        return {CONSTS.MESSAGE: CONSTS.GAME_STOPPED}

    def define_routes(self):
        @self.app.get(CONSTS.START_ENDPOINT)
        async def start_endpoint(pong_time_ms: int, second_server_port: int):
            message = await self.start_game(pong_time_ms=pong_time_ms, second_server_port=second_server_port)
            return message

        @self.app.get(CONSTS.PAUSE_ENDPOINT)
        async def pause_endpoint():
            message = self.pause_game()
            return message

        @self.app.get(CONSTS.RESUME_ENDPOINT)
        async def resume_endpoint():
            message = await self.resume_game()
            return message

        @self.app.get(CONSTS.STOP_ENDPOINT)
        async def stop_endpoint():
            message = await self.stop_game()
            return message

        @self.app.get(CONSTS.PING_ENDPOINT)
        async def handle_ping(sender_port: int):
            return await self.handle_ping_request(sender_port=sender_port)


def start_servers():
    server1 = Server(CONSTS.SERVER1_PORT)
    server2 = Server(CONSTS.SERVER2_PORT)

    server1_process = Process(target=server1.run)
    server2_process = Process(target=server2.run)

    server1_process.start()
    server2_process.start()

    server1_process.join()
    server2_process.join()


if __name__ == "__main__":
    start_servers()
