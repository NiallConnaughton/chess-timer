# Chess Timer — Requirements

A simple, kid-friendly chess clock website built for playing with my son.

---

## Modes

### Two-Player Mode (default)
- Each player has an independently configurable time budget (supports handicap naturally).
- Both clocks count down; the active player's clock runs, the other's pauses.
- The game ends when either player's clock reaches zero.

### Single-Clock Mode
- Only one player (the parent) has a running clock.
- The other player's (the child's) "side" is displayed but no timer counts down for them.
- Useful when teaching or when the child plays at their own pace.

---

## Controls

| Action | Input |
|---|---|
| Switch active player | Spacebar, tap the active player's panel, or the switch button |
| Start / Resume game | Spacebar or start button (from setup or pause) |
| Pause game | Dedicated pause button |
| Reset / New game | Button that returns to setup screen |

---

## UI / UX

### Layout
- Two large panels filling the screen (top/bottom split on portrait, left/right on landscape).
- A single prominent switch button sits centered on the divider between the two panels.
- The active player's panel is visually highlighted: rich blue background with a colored inset border.
- The inactive player's panel has a near-black background to maximise contrast.
- Timer display is large, centered in each panel.

### Timer Color Cues
| State | Condition | Color |
|---|---|---|
| Normal | > 2 minutes remaining | White |
| Warning | ≤ 2 minutes remaining | Yellow |
| Critical | ≤ 1 minute remaining | Red |

(Thresholds are constants in the code, easy to adjust.)

### Chess Theming
- Chess piece icons (♔ white king, ♚ black king) appear next to player labels on the setup screen and inside each panel on the game screen.
- The switch button uses a knight icon (♞).

### General Style
- Clean, minimal design — no distracting animations beyond color changes.
- High contrast; works in both bright and dim lighting.
- Large tap targets suitable for a child.

---

## Screens / Views

### 1. Setup Screen
- Select mode: Two-Player or Single-Clock.
- Name input for each player (defaults to "Player 1" / "Player 2").
- Set time for Player 1 (parent) — common presets plus a custom input.
- Set time for Player 2 (child) — same options (grayed out in Single-Clock mode).
- "Start Game" button.
- Preset options: 1 min, 3 min, 5 min, 10 min, 15 min, 30 min, custom.

### 2. Game Screen
- Two panels with running timers and player name/piece icon.
- Prominent switch button centered on the divider between panels.
- Pause button and "New Game" button in a thin header bar.

### 3. Game Over State
- No overlay. The losing player's panel turns yellow and shows 0:00.
- The other panel stays as-is. Players decide when they want a new game.
- "New Game" button in the header returns to setup.

---

## Non-Goals (out of scope for now)
- Per-move increments (Fischer) or delay (Bronstein).
- Move counter or move history.
- Sound effects.
- Accounts, score tracking, or persistence between sessions.
- Mobile app (web only, but should be mobile-friendly in browser).
