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
| Switch active player | Spacebar or tap the active player's panel |
| Start / Resume game | Spacebar or start button (from setup or pause) |
| Pause game | Dedicated pause button |
| Reset / New game | Button that returns to setup screen |

---

## UI / UX

### Layout
- Two large panels filling the screen (top/bottom split on portrait, left/right on landscape).
- The active player's panel is visually highlighted (distinct background color or border).
- The inactive player's panel is dimmed.
- Timer display is large, centered in each panel.

### Timer Color Cues
| State | Condition | Color |
|---|---|---|
| Normal | > 30 seconds remaining | White |
| Warning | ≤ 30 seconds remaining | Yellow |
| Critical | ≤ 10 seconds remaining | Red |

(Thresholds should be constants in the code, easy to adjust.)

### General Style
- Clean, minimal design — no distracting animations beyond color changes.
- High contrast; works in both bright and dim lighting.
- Large tap targets suitable for a child.

---

## Screens / Views

### 1. Setup Screen
- Select mode: Two-Player or Single-Clock.
- Set time for Player 1 (parent) — common presets plus a custom input.
- Set time for Player 2 (child) — same options (hidden / grayed out in Single-Clock mode).
- "Start Game" button.
- Preset options: 1 min, 3 min, 5 min, 10 min, 15 min, 30 min, custom.

### 2. Game Screen
- Two panels with running timers.
- Pause button (small, unobtrusive).
- "New Game" button to return to setup.
- No other chrome.

### 3. Game Over State
- Overlay or panel change indicating which player ran out of time.
- "Play Again" button (returns to setup with same settings pre-filled).

---

## Non-Goals (out of scope for now)
- Per-move increments (Fischer) or delay (Bronstein).
- Move counter or move history.
- Sound effects.
- Accounts, score tracking, or persistence between sessions.
- Mobile app (web only, but should be mobile-friendly in browser).
