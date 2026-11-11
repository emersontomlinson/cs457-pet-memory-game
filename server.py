import argparse
import socket
import threading
import time

from game import PetMemoryGame
from protocol import receive_messages, send_message


GAME = PetMemoryGame()
CLIENTS = {}

STATE_LOCK = threading.Lock()
BROADCAST_LOCK = threading.Lock()

GAME_RUNNING = False


def valid_port(value):
    port = int(value)

    if port < 1024 or port > 65535:
        raise argparse.ArgumentTypeError(
            "Port must be between 1024 and 65535."
        )

    return port


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pet Memory Match game server."
    )
    parser.add_argument(
        "-p",
        "--port",
        required=True,
        type=valid_port,
        help="Port for the server to listen on.",
    )
    return parser.parse_args()


def make_message(message_type, payload):
    return {
        "msg_type": message_type,
        "player_id": "SERVER",
        "payload": payload,
        "timestamp": int(time.time()),
    }


def send_to_client(client, message):
    try:
        with client["send_lock"]:
            send_message(client["socket"], message)
    except OSError:
        pass


def broadcast(message):
    with BROADCAST_LOCK:
        with STATE_LOCK:
            recipients = list(CLIENTS.values())

        for client in recipients:
            send_to_client(client, message)


def current_state(revealed=(), message=""):
    return {
        "board": GAME.board_view(revealed),
        "scores": GAME.scores.copy(),
        "active_player": GAME.active_player,
        "message": message,
    }


def send_error(client, code, message):
    send_to_client(
        client,
        make_message(
            "ERROR",
            {
                "code": code,
                "message": message,
            },
        ),
    )


def start_game():
    global GAME_RUNNING

    with STATE_LOCK:
        player_ids = list(CLIENTS.keys())
        GAME.start(player_ids[0], player_ids[1])
        GAME_RUNNING = True

        players = {
            player_id: CLIENTS[player_id]["alias"]
            for player_id in player_ids
        }

        game_start = make_message(
            "GAME_START",
            {
                "players": players,
                "active_player": GAME.active_player,
            },
        )
        state_update = make_message(
            "STATE_UPDATE",
            current_state(message="Game started. Player_1 goes first."),
        )

    broadcast(game_start)
    broadcast(state_update)


def handle_connect(client_socket, alias):
    with STATE_LOCK:
        if len(CLIENTS) >= 2:
            return None, "The game already has two players."

        player_id = f"Player_{len(CLIENTS) + 1}"
        client = {
            "socket": client_socket,
            "alias": alias,
            "send_lock": threading.Lock(),
        }
        CLIENTS[player_id] = client
        player_count = len(CLIENTS)

    if player_count == 1:
        send_to_client(
            client,
            make_message(
                "LOBBY_WAIT",
                {"message": "Waiting for Player 2."},
            ),
        )
    else:
        start_game()

    return player_id, None


def handle_move(player_id, client, positions):
    global GAME_RUNNING

    with STATE_LOCK:
        if not GAME_RUNNING:
            error_code = "MALFORMED_MESSAGE"
            error_message = "The game has not started yet."
        else:
            error_code = GAME.validate_move(player_id, positions)

            if error_code == "NOT_YOUR_TURN":
                error_message = "It is not your turn."
            elif error_code == "INVALID_POSITION":
                error_message = "Choose positions from A1 through B4."
            elif error_code == "DUPLICATE_POSITION":
                error_message = "Choose two different card positions."
            elif error_code == "CARD_ALREADY_MATCHED":
                error_message = "One of those cards is already matched."
            elif error_code == "MALFORMED_MESSAGE":
                error_message = "Choose exactly two card positions."
            else:
                error_message = ""

        if error_code:
            result = None
        else:
            result = GAME.evaluate_move(player_id, positions)

            revealed_update = make_message(
                "STATE_UPDATE",
                current_state(
                    revealed=result["revealed"],
                    message="Cards revealed.",
                ),
            )

            if result["game_over"]:
                GAME_RUNNING = False
                scores = GAME.scores.copy()

                if scores["Player_1"] == scores["Player_2"]:
                    outcome = "tie"
                    winner = None
                    reason = "The game ended in a tie."
                else:
                    outcome = "win"
                    winner = max(scores, key=scores.get)
                    reason = f"{winner} found the most pairs."

                game_over = make_message(
                    "GAME_OVER",
                    {
                        "outcome": outcome,
                        "winner": winner,
                        "final_scores": scores,
                        "reason": reason,
                    },
                )
            else:
                game_over = None

    if error_code:
        send_error(client, error_code, error_message)
        return

    broadcast(revealed_update)

    if result["is_match"]:
        update = make_message(
            "STATE_UPDATE",
            current_state(message=f"{player_id} found a match."),
        )
        broadcast(update)
    elif not result["game_over"]:
        time.sleep(2)

        with STATE_LOCK:
            hidden_update = make_message(
                "STATE_UPDATE",
                current_state(
                    message=f"No match. {GAME.active_player}'s turn.",
                ),
            )

        broadcast(hidden_update)

    if game_over:
        broadcast(game_over)


def remove_client(player_id):
    global GAME_RUNNING

    with STATE_LOCK:
        if player_id not in CLIENTS:
            return

        del CLIENTS[player_id]

        if GAME_RUNNING and CLIENTS:
            GAME_RUNNING = False
            remaining_player = next(iter(CLIENTS))
            scores = GAME.scores.copy()

            game_over = make_message(
                "GAME_OVER",
                {
                    "outcome": "forfeit",
                    "winner": remaining_player,
                    "final_scores": scores,
                    "reason": "The other player disconnected.",
                },
            )
        else:
            game_over = None

    if game_over:
        broadcast(game_over)


def handle_client(client_socket, client_address):
    buffer = b""
    player_id = None
    client = None

    print(f"Client connected from {client_address}.")

    try:
        while True:
            messages, buffer = receive_messages(client_socket, buffer)

            if messages is None:
                break

            for message in messages:
                message_type = message.get("msg_type")
                payload = message.get("payload", {})

                if message_type == "CONNECT" and player_id is None:
                    alias = payload.get("alias", "Player")
                    player_id, error = handle_connect(client_socket, alias)

                    if error:
                        send_message(
                            client_socket,
                            make_message(
                                "ERROR",
                                {
                                    "code": "GAME_FULL",
                                    "message": error,
                                },
                            ),
                        )
                        return

                    with STATE_LOCK:
                        client = CLIENTS[player_id]

                    print(f"{player_id} joined as {alias}.")

                elif message_type == "MOVE" and player_id:
                    handle_move(
                        player_id,
                        client,
                        payload.get("positions"),
                    )

                elif message_type == "DISCONNECT":
                    return

                elif player_id:
                    send_error(
                        client,
                        "MALFORMED_MESSAGE",
                        "Unknown or invalid message.",
                    )

    except (ConnectionResetError, ValueError, OSError) as error:
        print(f"Client error from {client_address}: {error}")

    finally:
        if player_id:
            remove_client(player_id)

        client_socket.close()
        print(f"Client disconnected: {client_address}.")


def main():
    args = parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", args.port))
        server_socket.listen()

        print(f"Pet Memory Match server listening on port {args.port}.")
        print("Waiting for players...")

        while True:
            client_socket, client_address = server_socket.accept()

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True,
            )
            client_thread.start()


if __name__ == "__main__":
    main()