# Pet Memory Match FSM

```mermaid
stateDiagram-v2
    [*] --> INIT
    INIT --> WAITING_FOR_PLAYERS: Start server

    WAITING_FOR_PLAYERS --> WAITING_FOR_PLAYERS: First CONNECT / LOBBY_WAIT
    WAITING_FOR_PLAYERS --> GAME_START: Second CONNECT
    WAITING_FOR_PLAYERS --> CLEANUP: Player disconnects

    GAME_START --> PLAYER_TURN: Shuffle cards / assign Player_1 and Player_2

    PLAYER_TURN --> EVALUATE_MOVE: Valid MOVE from active player
    PLAYER_TURN --> PLAYER_TURN: Bad or out-of-turn MOVE / ERROR
    PLAYER_TURN --> GAME_OVER: Disconnect or network drop / forfeit

    EVALUATE_MOVE --> PLAYER_TURN: Match / score and same turn
    EVALUATE_MOVE --> PLAYER_TURN: No match / hide cards and switch turn
    EVALUATE_MOVE --> GAME_OVER: All pairs found

    GAME_OVER --> CLEANUP: Send GAME_OVER
    CLEANUP --> WAITING_FOR_PLAYERS: Clear state
```

- `INIT`: Start the server.
- `WAITING_FOR_PLAYERS`: Wait for two clients.
- `GAME_START`: Shuffle eight cards, assign players, and set scores to zero.
- `PLAYER_TURN`: Wait for the active player’s move.
- `EVALUATE_MOVE`: Check the two selected cards and send `STATE_UPDATE`.
- `GAME_OVER`: Send the final win, tie, or forfeit result.
- `CLEANUP`: Close sockets, clear state, and return to the lobby.

Invalid, duplicate, already matched, malformed, and out-of-turn moves send `ERROR` and stay in `PLAYER_TURN`. A normal disconnect, TCP EOF, or socket error counts as a disconnect. An in-game disconnect gives the opponent a forfeit win.
