# AI Prompt

I will use Codex to help write the code, but not let it direct or come up with the main project components.

```text
Follow docs/protocol_blueprint.md and docs/fsm_specification.md exactly.

Use Python TCP with UTF-8 newline-delimited JSON. Every sent JSON message must end with \n. Incoming TCP bytes must be buffered until a complete newline-terminated message is available.

Use only CONNECT, LOBBY_WAIT, GAME_START, MOVE, STATE_UPDATE, ERROR, DISCONNECT, and GAME_OVER. Do not rename or add messages.

The server controls the board, scores, matches, and turns. Reject bad or out-of-turn moves with ERROR. Treat b"" as EOF and handle ConnectionResetError, BrokenPipeError, and ConnectionAbortedError as disconnects.

Before writing code, say which protocol rule or FSM transition the code follows.
```

I will check that AI-generated code follows these files before using it.
