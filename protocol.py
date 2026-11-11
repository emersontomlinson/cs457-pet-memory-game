import json


def send_message(sock, message):
    data = json.dumps(message).encode("utf-8") + b"\n"
    sock.sendall(data)


def receive_messages(sock, buffer):
    data = sock.recv(4096)

    if not data:
        return None, buffer

    buffer += data
    messages = []

    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)

        if line:
            messages.append(json.loads(line.decode("utf-8")))

    return messages, buffer