# CS 457 Project Statement of Work (SOW) & Protocol Specification Template

**Student Name:** Emerson Tomlinson  
**Date:** 2026-09-19  
**Course:** CS 457 - Computer Networks  
**Target Server Domain:** `server.tomlinson.edu`

---

## 1. Game Selection & Scope (Sprint 0)

> Planning is going to be an iterative process through the sprints so you don't have to have all the details now. Focus on big overview concepts. You will be updating the SOW as we plan.
> You have a lot of freedom to choose a game. There are a couple caveats.  

> - It must run in the console. The lab nodes won't be able to handle extensive graphics.
> - It has to be self-contained. You can use a internet-connector to download you code, but because the architecture must run 5 nodes you won't be able to run 
> - You are encouraged to use python, but I'm not going to make it a strict requirement. The instructor and TA's ability to help with C or Rust, etc will be diminished in other languages.

### 1.1 Game Overview
- **Chosen Game:** Pet Memory Matching Game
- **Player Capacity:** 2 Players (Simulated via 2 CML Client nodes)
- **Game Summary:** Pet Memory Match is a two-player, terminal-based memory matching game featuring my four pets. The server shuffles eight hidden cards containing two cards for each pet name. Players alternate choosing two hidden card positions. Both players see the revealed cards. If the chosen cards match, the active player earns one point and takes another turn. If they do not match, the cards are hidden again and the turn passes to the other player.

### 1.2 Core Game Rules & Win/Draw Conditions
- **Turn Mechanics:** Once two players connect, the server assigns Player 1 and Player 2. Player 1 takes the first turn. The active player selects two different hidden card positions. The server validates the selections, reveals both cards to both players, and determines whether they match. A matching pair earns one point and gives the player another turn. A non-matching pair is hidden after being shown, and the turn switches to the other player.
- **Victory Condition:** The game ends after all four matching pairs have been found. The player with the most matched pairs wins.
- **Draw/Tie Condition:** If all four matching pairs have been found and both players have the same score, the game ends in a tie.

---

## 2. Application-Layer Messaging Protocol Blueprint (Sprint 1 Deliverable)

### 2.1 Message Transport & Serialization Format
- **Transport Protocol:** TCP
- **Serialization Format:** [JSON / Fixed-Header Binary / Delimited Text]
- **Framing Mechanism:** [e.g., Newline-delimited (`\n`) JSON payloads OR 4-byte big-endian length prefix]

### 2.2 Message Schema Definitions

#### Message Types:
1. `CONNECT` (Client -> Server): Request to join the game room.
2. `LOBBY_WAIT` (Server -> Client): Notification that server is waiting for Player 2.
3. `GAME_START` (Server -> Clients): Game initiated, assigns roles (e.g. Player X vs Player O).
4. `MOVE` (Client -> Server): Player action (e.g., cell coordinates or answer choice).
5. `STATE_UPDATE` (Server -> Clients): Broadcast current game board / state and active player turn.
6. `GAME_OVER` (Server -> Clients): Victory / Draw notification with final scores.
7. `ERROR` (Server -> Client): Invalid move or malformed packet error.

#### Example JSON Protocol Schema:
```json
{
  "msg_type": "MOVE",
  "player_id": "Player_1",
  "payload": {
    "row": 0,
    "col": 2
  },
  "timestamp": 1727000000
}
```

---

### 2.3 Game State Machine (FSM) Design (Sprint 1 Deliverable)
- **State Transitions:** Detail state flow: `INIT` -> `WAITING_FOR_PLAYERS` -> `PLAYER_TURN` -> `EVALUATE_MOVE` -> `CHECK_WIN_DRAW` -> `GAME_OVER` -> `CLEANUP`.

---

## 3. Game Behavior & Server Concurrency Architecture (Sprint 2 Deliverable)

### 3.1 Server Concurrency Strategy
- **Architecture Choice:** [Multi-Threading (`threading.Thread`) OR Non-blocking I/O multiplexing (`select.select` / `selectors`)]
- **Synchronization Logic:** Explain how shared game state and client list are thread-safe (e.g. `threading.Lock`) to prevent race conditions during turn processing.

### 3.2 State & Score Synchronization Across Clients
- **Turn Enforcement:** Detail how the server validates active player ID before processing moves and broadcasts updated turn notifications to all clients.
- **Score & Board Synchronization:** Describe how state broadcasts keep client screens synchronized in real time.

---

## 4. Coding & AI Implementation Plan (Sprint 3)

- **Permitted AI Tools:** [e.g., GitHub Copilot, ChatGPT, Claude]
- **AI Prompting & Constraint Strategy:** Explain how you will constrain AI models to generate code (in Python or your chosen language) that adheres strictly to the protocol blueprint and FSM designed in Sprints 1 & 2.
- **Implementation Risk Management:** Detail your plan to leverage past programming experience and manage time to ensure code completion on schedule.

---

## 5. CML Multi-Subnet Topology & Wireshark Deployment Plan (Sprint 4 & 5 Deliverable)

> For now you can use the topology below. We may update this when we get to defining subnets.

### 5.1 Subnet & Router Design
- **Subnet A (Client 1):** `192.168.10.0/24` (Interface `Gi0/1` on Router R1)
- **Subnet B (Client 2):** `192.168.11.0/24` (Interface `Gi0/2` on Router R1)
- **Subnet C (Game Server):** `192.168.20.0/24` (Interface `Gi0/1` on Router R2)
- **Router Backbone:** `10.0.0.0/30` (Interface `Gi0/0` on R1 <-> `Gi0/0` on R2)

### 5.2 DHCP Pools & DNS Configuration Plan
- **Router R1 DHCP Pool 1 (`CLIENT1_POOL`):** Leases `192.168.10.10` - `192.168.10.50`, gateway `192.168.10.1`, DNS `10.0.0.2`.
- **Router R1 DHCP Pool 2 (`CLIENT2_POOL`):** Leases `192.168.11.10` - `192.168.11.50`, gateway `192.168.11.1`, DNS `10.0.0.2`.
- **Router R2 Authoritative DNS:** Configured with `ip dns server` and static host mapping `server.[yourlastname].edu` -> `192.168.20.100`.

### 5.3 Deployment Strategy & Wireshark Trace Capture
- **CML Deployment Strategy:** Deploy `server.py` onto Subnet C node (`192.168.20.100`) behind Router R2, and `client.py` onto Subnet A and Subnet B nodes behind Router R1.
- **Cisco Infrastructure Configuration:** Router R1 DHCP pools (`CLIENT1_POOL`, `CLIENT2_POOL`) and Router R2 authoritative DNS (`ip host server.[lastname].edu 192.168.20.100`).
- **Wireshark Trace Capture Plan:** Capture DHCP DORA exchange (`dhcp_negotiation.pcap`) and DNS query/response resolution (`dns_lookup.pcap`).

- ## 4. Server-to-Client Message Types

### 4.1 `LOBBY_WAIT`

- **Direction:** Server → Client
- **Purpose:** Tells the first connected player that the server is waiting for a second player.
- **Payload fields:**
  - `message` (string): Lobby status message.
  - `connected_players` (integer): Number of currently connected players.

```json
{
  "msg_type": "LOBBY_WAIT",
  "player_id": "SERVER",
  "payload": {
    "message": "Waiting for another player to connect.",
    "connected_players": 1
  },
  "timestamp": 1790000001
}
```

### 4.2 `GAME_START`

- **Direction:** Server → Both Clients
- **Purpose:** Starts a new game and assigns Player 1 and Player 2.
- **Payload fields:**
  - `players` (object): Maps player IDs to display names.
  - `active_player` (string): The player ID allowed to make the first move.
  - `board_rows` (integer): Number of board rows.
  - `board_columns` (integer): Number of board columns.

```json
{
  "msg_type": "GAME_START",
  "player_id": "SERVER",
  "payload": {
    "players": {
      "Player_1": "Emerson",
      "Player_2": "Opponent"
    },
    "active_player": "Player_1",
    "board_rows": 2,
    "board_columns": 4
  },
  "timestamp": 1790000002
}
```

### 4.3 `STATE_UPDATE`

- **Direction:** Server → Both Clients
- **Purpose:** Broadcasts the current board display, scores, and active player after a valid move.
- **Payload fields:**
  - `board` (object): Maps each position (`A1` through `B4`) to either `HIDDEN` or a pet name.
  - `scores` (object): Maps player IDs to integer scores.
  - `active_player` (string): The player ID whose turn is next.
  - `message` (string): A brief result, such as `Match found` or `No match`.

```json
{
  "msg_type": "STATE_UPDATE",
  "player_id": "SERVER",
  "payload": {
    "board": {
      "A1": "Cordelia",
      "A2": "HIDDEN",
      "A3": "HIDDEN",
      "A4": "HIDDEN",
      "B1": "HIDDEN",
      "B2": "Cordelia",
      "B3": "HIDDEN",
      "B4": "HIDDEN"
    },
    "scores": {
      "Player_1": 1,
      "Player_2": 0
    },
    "active_player": "Player_1",
    "message": "Match found. Player_1 takes another turn."
  },
  "timestamp": 1790000006
}
```

### 4.4 `ERROR`

- **Direction:** Server → Client
- **Purpose:** Rejects an invalid, malformed, duplicate, already matched, or out-of-turn move without ending the game.
- **Payload fields:**
  - `code` (string): One of `NOT_YOUR_TURN`, `INVALID_POSITION`, `DUPLICATE_POSITION`, `CARD_ALREADY_MATCHED`, or `MALFORMED_MESSAGE`.
  - `message` (string): A player-readable explanation.

```json
{
  "msg_type": "ERROR",
  "player_id": "SERVER",
  "payload": {
    "code": "NOT_YOUR_TURN",
    "message": "It is currently Player_1's turn."
  },
  "timestamp": 1790000007
}
```

### 4.5 `GAME_OVER`

- **Direction:** Server → Both Clients
- **Purpose:** Announces the final outcome when all pairs are found or a player forfeits.
- **Payload fields:**
  - `outcome` (string): Either `win`, `tie`, or `forfeit`.
  - `winner` (string or null): Winning player ID, or `null` for a tie.
  - `final_scores` (object): Maps player IDs to final integer scores.
  - `reason` (string): Explains why the game ended.

```json
{
  "msg_type": "GAME_OVER",
  "player_id": "SERVER",
  "payload": {
    "outcome": "win",
    "winner": "Player_1",
    "final_scores": {
      "Player_1": 3,
      "Player_2": 1
    },
    "reason": "All four pairs have been found."
  },
  "timestamp": 1790000015
}
```
