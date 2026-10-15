# Pet Memory Match Concurrency Design

## Concurrency Model

This game will use Python multi-threading. The server will make one thread for each connected client so both players can stay connected without blocking each other.

The server will use one `threading.Lock` to protect the board, matched cards, scores, active player, and connected-client list.
