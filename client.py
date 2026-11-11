import argparse
import socket
import sys
import threading
import time

from protocol import receive_messages, send_message


def valid_port(value):
    port = int(value)

    if port < 1024 or port > 65535:
        raise argparse.ArgumentTypeError(
            "Port must be between 1024 and 65535."
        )

    return port


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pet Memory Match game client."
    )
    parser.add_argument(
        "-i",
        "--host",
        required=True,
        help="Server hostname or IP address.",
    )
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        type=valid_port,
        help="Server port number.",
    )
    return parser.parse_args()


def make_message(message_type, player_id, payload):
    return {
        "msg_type": message_type,
        "player_id": player_id,
        "payload": payload,
        "timestamp": int(time.time()),
    }


def display_board(board):
    print()
    print("         A           B")

    for row in ("1", "2", "3", "4"):
        cards = []

        for column in ("A", "B"):
            value = board[f"{column}{row}"]
            cards.append(f"[{value:^10}]")

        print(f"Row {row}  " + " ".join(cards))

    print()


def listen_for_messages(client_socket, alias, client_state, state_lock, done):
    buffer = b""

    try:
        while not done.is_set():
            messages, buffer = receive_messages(client_socket, buffer)

            if messages is None:
                print("\nDisconnected from the server.")
                done.set()
                break

            for message in messages:
                message_type = message["msg_type"]
                payload = message["payload"]

                if message_type == "LOBBY_WAIT":
                    print(payload["message"])

                elif message_type == "GAME_START":
                    for player_id, player_alias in payload["players"].items():
                        if player_alias == alias:
                            with state_lock:
                                client_state["player_id"] = player_id

                    print("\nGame started.")

                elif message_type == "STATE_UPDATE":
                    display_board(payload["board"])
                    print(f"Scores: {payload['scores']}")
                    print(payload["message"])

                    with state_lock:
                        if payload["message"] == "Cards revealed.":
                            client_state["my_turn"] = False
                        else:
                            client_state["my_turn"] = (
                                payload["active_player"]
                                == client_state["player_id"]
                            )

                    if client_state["my_turn"]:
                        print("Your turn.")
                    else:
                        print("Waiting for the other player.")

                elif message_type == "ERROR":
                    print(f"[ERROR] {payload['message']}")

                    retry_codes = {
                        "INVALID_POSITION",
                        "DUPLICATE_POSITION",
                        "CARD_ALREADY_MATCHED",
                        "MALFORMED_MESSAGE",
                    }

                    if payload["code"] in retry_codes:
                        with state_lock:
                            client_state["my_turn"] = True

                        print("Try again.")

                elif message_type == "GAME_OVER":
                    print("\nGame over.")
                    print(f"Final scores: {payload['final_scores']}")
                    print(payload.get("reason", ""))
                    done.set()
                    break

    except (ConnectionResetError, OSError, ValueError) as error:
        print(f"\n[ERROR] Connection problem: {error}")
        done.set()


def main():
    args = parse_args()
    alias = input("Enter your name: ").strip() or "Player"

    try:
        server_ip = socket.gethostbyname(args.host)
    except socket.gaierror:
        print(f"[ERROR] Unable to resolve hostname: {args.host}")
        print("Check the server name or DNS configuration.")
        return 1

    done = threading.Event()
    state_lock = threading.Lock()
    client_state = {
        "player_id": None,
        "my_turn": False,
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, args.port))

            send_message(
                client_socket,
                make_message(
                    "CONNECT",
                    "UNASSIGNED",
                    {"alias": alias},
                ),
            )

            print(f"Connected to {args.host} ({server_ip}) on port {args.port}.")

            listener = threading.Thread(
                target=listen_for_messages,
                args=(
                    client_socket,
                    alias,
                    client_state,
                    state_lock,
                    done,
                ),
                daemon=True,
            )
            listener.start()

            while not done.is_set():
                with state_lock:
                    my_turn = client_state["my_turn"]
                    player_id = client_state["player_id"]

                if not my_turn:
                    time.sleep(0.1)
                    continue

                move = input("Choose two cards, such as A1 B2, or type quit: ")
                move = move.strip()

                if move.lower() == "quit":
                    send_message(
                        client_socket,
                        make_message(
                            "DISCONNECT",
                            player_id,
                            {"reason": "user_exit"},
                        ),
                    )
                    done.set()
                    break

                positions = move.upper().split()

                send_message(
                    client_socket,
                    make_message(
                        "MOVE",
                        player_id,
                        {"positions": positions},
                    ),
                )

                with state_lock:
                    client_state["my_turn"] = False

    except OSError as error:
        print(f"[ERROR] Could not connect to the server: {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())