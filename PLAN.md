# Chess Timer — Implementation Plan

## Tech Stack
- **Plain HTML / CSS / JS** — no build step, no dependencies.
- Deployable directly via GitHub Pages.

---

## File Structure

```
chess-timer/
├── index.html        # Single page app shell
├── style.css         # All styles
├── app.js            # All logic
├── REQUIREMENTS.md
└── PLAN.md
```

---

## Implementation Phases

### Phase 1 — Core timer engine (`app.js`)
- `GameState` object: mode, times, active player, running/paused/over flags.
- `tick()` function driven by `setInterval` (100ms resolution).
- `switchPlayer()` — pauses current clock, starts other.
- `pause()` / `resume()`.
- `reset()` — clears interval, resets to setup.
- Spacebar listener attached at document level.

### Phase 2 — Setup screen
- Mode selector (two buttons or a toggle).
- Time picker per player: row of preset buttons + a number input for custom.
- Player 2 controls hidden/disabled in Single-Clock mode.
- Validates inputs before enabling Start.

### Phase 3 — Game screen
- Two `<div>` panels, each containing:
  - Player label.
  - Large time display (MM:SS).
- Active panel gets `.active` class (highlight color).
- Timer text gets `.warning` or `.critical` class based on remaining time.
- Pause button and New Game button in a small header/footer strip.

### Phase 4 — Game over
- When a clock hits zero: stop interval, show game-over overlay.
- Overlay names the player who ran out, offers "Play Again."
- "Play Again" restores last-used settings on setup screen.

### Phase 5 — Polish & responsiveness
- Portrait (mobile): panels stacked top/bottom.
- Landscape (mobile/tablet): panels side by side.
- Desktop: either orientation, panels fill viewport.
- Visual review: color scheme, font sizes, tap target sizes.

---

## Key Constants (in `app.js`)
```js
const WARNING_THRESHOLD_MS = 30_000;  // 30 seconds
const CRITICAL_THRESHOLD_MS = 10_000; // 10 seconds
const TICK_INTERVAL_MS = 100;
```

---

## Color Palette (proposed, adjustable)
| Role | Color |
|---|---|
| Background | `#1a1a2e` (dark navy) |
| Inactive panel | `#16213e` |
| Active panel | `#0f3460` |
| Timer text (normal) | `#e0e0e0` |
| Timer text (warning) | `#f5c518` (yellow) |
| Timer text (critical) | `#e63946` (red) |
| Accent / buttons | `#e94560` |

---

## Deployment
- Enable GitHub Pages on the `main` branch (`/` root).
- No build step needed — push and it's live.
