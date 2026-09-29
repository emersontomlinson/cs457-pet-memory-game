# Pet Memory Match Protocol

## Format

- **Transport:** TCP
- **Message format:** UTF-8 JSON
- **Framing:** Every JSON message ends with `\n`.

TCP is a stream, so the receiver keeps incoming bytes in a buffer and parses a message only when it finds `\n`.

```text
{"msg_type":"CONNECT","player_id":"UNASSIGNED","payload":{"alias":"Emerson"},"timestamp":1790000000}\n{"msg_type":"MOVE","player_id":"Player_1","payload":{"positions":["A1","B2"]},"timestamp":1790000005}\n
```

Every message has `msg_type` (string), `player_id` (string), `payload` (object), and `timestamp` (integer).

## Messages

| Type | Direction | Purpose | Payload fields and types |
| --- | --- | --- | --- |
| `CONNECT` | Client → Server | Join the game | `alias`: string |
| `LOBBY_WAIT` | Server → Client | Wait for Player 2 | `message`: string |
| `GAME_START` | Server → Both Clients | Start game and assign players | `players`: object, `active_player`: string |
| `MOVE` | Client → Server | Select two cards | `positions`: array of two different strings from `A1`–`B4` |
| `STATE_UPDATE` | Server → Both Clients | Send current game state | `board`: object mapping `A1`–`B4` to `HIDDEN` or pet names; `scores`: object of player IDs to integers; `active_player`: string; `message`: string |
| `ERROR` | Server → Client | Reject a bad request | `code`: string; `message`: string |
| `DISCONNECT` | Client → Server | Leave the game | `reason`: string |
| `GAME_OVER` | Server → Both Clients | Send final result | `outcome`: string (`win`, `tie`, or `forfeit`); `winner`: string or `null`; `final_scores`: object |

## Sample Payloads

```text
CONNECT: {"alias":"Emerson"}
LOBBY_WAIT: {"message":"Waiting for Player 2."}
GAME_START: {"players":{"Player_1":"Emerson","Player_2":"Opponent"},"active_player":"Player_1"}
MOVE: {"positions":["A1","B2"]}
STATE_UPDATE: {"board":{"A1":"Cordelia","A2":"HIDDEN","A3":"HIDDEN","A4":"HIDDEN","B1":"HIDDEN","B2":"Cordelia","B3":"HIDDEN","B4":"HIDDEN"},"scores":{"Player_1":1,"Player_2":0},"active_player":"Player_1","message":"Match found."}
ERROR: {"code":"NOT_YOUR_TURN","message":"It is Player_1's turn."}
DISCONNECT: {"reason":"user_exit"}
GAME_OVER: {"outcome":"win","winner":"Player_1","final_scores":{"Player_1":3,"Player_2":1}}
```

## Disconnects

- A client sends `DISCONNECT`, then closes its socket normally with TCP FIN.
- `recv()` returning `b""` means TCP EOF and a disconnected client.
- `ConnectionResetError`, `BrokenPipeError`, and `ConnectionAbortedError` mean an abrupt disconnect.
- An in-game disconnect gives the other player a forfeit win. A lobby disconnect returns the server to waiting.
