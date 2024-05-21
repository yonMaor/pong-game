import CONSTS


def build_request_url(server_port, endpoint):
    url = "".join([CONSTS.HTTP_LOCALHOST, str(server_port), endpoint])
    return url


def generate_ping_received_message(port, sender_port):
    return f"{port} has received ping from server {sender_port}"
