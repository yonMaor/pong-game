import argparse
import asyncio
import requests

import utils
import CONSTS

ports = (CONSTS.SERVER1_PORT, CONSTS.SERVER2_PORT)


def send_request_to_servers(request, server_ports, command_endpoint, request_params):
    if isinstance(server_ports, int):
        server_ports = [server_ports]
    for port in server_ports:
        try:
            response = request(utils.build_request_url(port, command_endpoint), params=request_params)
            if not response.status_code == 200:
                raise Exception
        except Exception as e:
            print("Error:", e)


def start_game(pong_time_ms: int):
    print("Starting game")
    send_request_to_servers(requests.get, server_ports=ports[0], command_endpoint=CONSTS.START_ENDPOINT,
                            request_params={"pong_time_ms": pong_time_ms, "second_server_port": ports[1]})
    send_request_to_servers(requests.get, server_ports=ports[1], command_endpoint=CONSTS.START_ENDPOINT,
                            request_params={"pong_time_ms": pong_time_ms, "second_server_port": ports[0]})

    # TODO: Instead of sending a ping here, start should receive another input which is which server goes first
    send_request_to_servers(requests.get, server_ports=ports[1], command_endpoint=CONSTS.PING_ENDPOINT,
                            request_params={"sender_port": CONSTS.SERVER1_PORT})


def pause_game():
    print("Pausing game")
    send_request_to_servers(request=requests.get, server_ports=ports, command_endpoint=CONSTS.PAUSE_ENDPOINT,
                            request_params={})


def resume_game():
    print("Resuming game")
    send_request_to_servers(request=requests.get, server_ports=ports, command_endpoint=CONSTS.RESUME_ENDPOINT,
                            request_params={})


def stop_game():
    print("Stopping game")
    send_request_to_servers(request=requests.get, server_ports=ports, command_endpoint=CONSTS.STOP_ENDPOINT,
                            request_params={})


async def main():
    parser = argparse.ArgumentParser(description='Pong game CLI tool')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to control the game')

    start_parser = subparsers.add_parser('start', help='Start the game with specified pong time')
    start_parser.add_argument('pong_time_ms', type=int, help='Time interval between pongs')

    subparsers.add_parser('pause', help='Pause the game')
    subparsers.add_parser('resume', help='Resume the game')
    subparsers.add_parser('stop', help='Stop the game')

    args = parser.parse_args()

    if args.command == 'start':
        print("Before start")
        start_game(args.pong_time_ms)
    elif args.command == 'pause':
        pause_game()
    elif args.command == 'resume':
        resume_game()
    elif args.command == 'stop':
        stop_game()


if __name__ == '__main__':
    asyncio.run(main())
