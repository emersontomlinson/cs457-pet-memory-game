# Protocol Blueprint: Pet Memory Match

## 1. Design Choices

- **Transport Protocol:** TCP
- **Serialization Format:** JSON encoded as UTF-8
- **Framing Rule:** Newline-delimited JSON
- **Server Role:** The server is authoritative. It stores the shuffled cards, revealed and matched cards, player scores, connected clients, and active turn.

### 1.1 TCP Framing Rule

TCP sends a continuous stream of bytes, not separate messages. Therefore, every JSON message sent by this game must be UTF-8 encoded and end with exactly one newline character (`\n`).

The receiver keeps incoming bytes in a buffer. Each time a newline is found, the receiver removes one complete line from the buffer and parses that line as one JSON message. Any remaining bytes stay in the buffer until another complete message arrives.

### 1.2 Wire Example

Two messages may arrive together in one TCP receive operation:

```text
{"msg_type":"CONNECT","player_id":"Player_1","payload":{"alias":"Emerson"}}\n{"msg_type":"MOVE","player_id":"Player_1","payload":{"positions":["A1","B2"]}}\n
```

A message may also arrive in pieces. The receiver must wait until it has received the newline before parsing the JSON message.

## 2. Common Message Format

Every message is a JSON object with these fields:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `msg_type` | string | Yes | The message kind, such as `CONNECT`, `MOVE`, or `STATE_UPDATE`. |
| `player_id` | string | Yes | The sender's assigned player ID: `Player_1`, `Player_2`, or `SERVER`. |
| `payload` | object | Yes | The message-specific data. |
| `timestamp` | integer | Yes | Unix time in seconds when the message was created. |

Example common message structure:

```json
{
  "msg_type": "MESSAGE_TYPE",
  "player_id": "Player_1",
  "payload": {},
  "timestamp": 1780000000
}
```
## 3. Client-to-Server Message Types

### 3.1 `CONNECT`

- **Direction:** Client → Server
- **Purpose:** Requests to join the game and provides the player's display name.
- **Payload fields:**
  - `alias` (string): Player-chosen name, 1–20 characters.

```json
{
  "msg_type": "CONNECT",
  "player_id": "UNASSIGNED",
  "payload": {
    "alias": "Emerson"
  },
  "timestamp": 1790000000
}
```

### 3.2 `MOVE`

- **Direction:** Client → Server
- **Purpose:** The active player selects exactly two different hidden card positions for one turn.
- **Payload fields:**
  - `positions` (array of two strings): Valid board positions: `A1`, `A2`, `A3`, `A4`, `B1`, `B2`, `B3`, or `B4`.

```json
{
  "msg_type": "MOVE",
  "player_id": "Player_1",
  "payload": {
    "positions": ["A1", "B2"]
  },
  "timestamp": 1790000005
}
```

### 3.3 `DISCONNECT`

- **Direction:** Client → Server
- **Purpose:** Notifies the server that a player is intentionally leaving the game.
- **Payload fields:**
  - `reason` (string): A short explanation, such as `quit` or `user_exit`.

```json
{
  "msg_type": "DISCONNECT",
  "player_id": "Player_2",
  "payload": {
    "reason": "user_exit"
  },
  "timestamp": 1790000010
}
```
