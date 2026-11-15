"""Helpers for newline-delimited JSON messages."""

import json


def send_message(sock, message):
    """Send one JSON message followed by a newline."""
    # The newline marks the end of one TCP message
    data = json.dumps(message).encode("utf-8") + b"\n"
    sock.sendall(data)


def receive_messages(sock, buffer):
    """Read available data and return complete JSON messages."""
    data = sock.recv(4096)

    if not data:
        return None, buffer

    buffer += data
    messages = []

    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)

        if line:
            messages.append(json.loads(line.decode("utf-8")))

    # Keep an incomplete message in the buffer for the next recv call
    return messages, buffer
