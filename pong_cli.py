import requests


def send_command(server_url, command, param=None):
    url = f"{server_url}/{command}"
    if param:
        url += f"/{param}"
    response = requests.get(url)
    print(f"Server response: {response.json()}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <command> <param (optional)>")
        print("Commands: start <pong_time_ms>, pause, resume, stop")
        exit(1)

    server_url = "http://localhost:5001"  # Replace with the actual server URL
    command = sys.argv[1]
    param = None
    if command == "start":
        print(sys.argv)
        if len(sys.argv) != 3:
            print("Usage: start <pong_time_ms>")
            exit(1)
        param = int(sys.argv[2])
    elif command in ("pause", "resume", "stop"):
        pass  # These commands don't require additional parameters
    else:
        print("Invalid command. Use start, pause, resume, or stop")
        exit(1)

    send_command(server_url, command, param)
