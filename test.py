#!/usr/bin/env python3
"""
Playwright smoke tests for the chess timer.
Run from the project root: python3 test.py
Screenshots land in screenshots/ next to this file.
"""

import asyncio
import os
import threading
import http.server
import functools
from playwright.async_api import async_playwright

PORT = 7821
SCREENSHOTS = os.path.join(os.path.dirname(__file__), "screenshots")


def start_server():
    os.makedirs(SCREENSHOTS, exist_ok=True)
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=os.path.dirname(__file__),
    )
    server = http.server.HTTPServer(("", PORT), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


async def run():
    server = start_server()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        errors = []
        page.on("console", lambda m: errors.append(f"CONSOLE {m.type}: {m.text}") if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"PAGE ERROR: {e}"))

        def shot(name):
            return os.path.join(SCREENSHOTS, name)

        await page.goto(f"http://localhost:{PORT}/")
        await page.wait_for_load_state("networkidle")

        # ── Setup screen ────────────────────────────────────────────────
        await page.screenshot(path=shot("01_setup.png"))
        print("✓ Setup screen loaded")

        assert await page.is_visible("#btn-two-player"),   "Two Player button missing"
        assert await page.is_visible("#btn-single-clock"), "Single Clock button missing"

        presets  = await page.locator(".preset-btn").count()
        selected = await page.locator(".preset-btn.selected").all_text_contents()
        assert presets == 12,              f"Expected 12 preset buttons, got {presets}"
        assert selected == ["5m", "5m"],   f"Expected both players on 5m, got {selected}"
        print(f"  Preset buttons: {presets}, pre-selected: {selected}")

        # ── Name inputs ─────────────────────────────────────────────────
        assert await page.is_visible("#p1-name-input"), "P1 name input missing"
        assert await page.is_visible("#p2-name-input"), "P2 name input missing"

        assert await page.get_attribute("#p1-name-input", "placeholder") == "Player 1"
        assert await page.get_attribute("#p2-name-input", "placeholder") == "Player 2"
        print("✓ Name inputs present with correct placeholders")

        # ── Chess piece icons on setup ──────────────────────────────────
        piece_icons = await page.locator(".piece-icon").all_text_contents()
        assert "♔" in piece_icons, "White king icon missing from setup"
        assert "♚" in piece_icons, "Black king icon missing from setup"
        print(f"  Chess pieces on setup: {piece_icons}")

        # ── Custom names flow through to game screen ─────────────────────
        await page.fill("#p1-name-input", "Dad")
        await page.fill("#p2-name-input", "Kid")
        await page.click("#start-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("02_game_start.png"))

        assert await page.text_content("#p1-name-display") == "Dad", "P1 name not shown"
        assert await page.text_content("#p2-name-display") == "Kid", "P2 name not shown"
        print("✓ Custom names shown on game screen")

        # ── Chess piece icons on game screen ────────────────────────────
        panel_pieces = await page.locator(".player-piece").all_text_contents()
        assert "♔" in panel_pieces, "White king missing from game panel"
        assert "♚" in panel_pieces, "Black king missing from game panel"
        print(f"  Chess pieces on game screen: {panel_pieces}")

        # ── P1 clock counts down, panel highlighted ─────────────────────
        p1_start = await page.text_content("#p1-time")
        await page.wait_for_timeout(2000)
        p1_after = await page.text_content("#p1-time")
        p1_class = await page.get_attribute("#p1-panel", "class")
        assert p1_after != p1_start,  "P1 clock did not tick"
        assert "active" in p1_class,  "P1 panel not highlighted"
        print(f"  P1 after 2s: {p1_after}  (panel: {p1_class})")

        # ── Switch button present and enabled while running ─────────────
        assert await page.is_visible("#switch-btn"),                        "Switch button missing"
        assert await page.get_attribute("#switch-btn", "disabled") is None, "Switch button should be enabled"
        print("✓ Switch button visible and enabled")

        # ── Switch button switches player ───────────────────────────────
        await page.click("#switch-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("03_p2_active_via_button.png"))
        assert "active" not in await page.get_attribute("#p1-panel", "class"), "P1 still active after switch"
        assert "active"     in await page.get_attribute("#p2-panel", "class"), "P2 not active after switch"
        print("✓ Switch button switches active player")

        # ── P2 clock counts down ────────────────────────────────────────
        p2_before = await page.text_content("#p2-time")
        await page.wait_for_timeout(1100)
        p2_after  = await page.text_content("#p2-time")
        assert p2_after != p2_before, "P2 clock did not tick"
        print(f"  P2 time: {p2_before} → {p2_after}")

        # ── Spacebar switches player ────────────────────────────────────
        await page.keyboard.press("Space")
        await page.wait_for_timeout(300)
        assert "active" in await page.get_attribute("#p1-panel", "class"), "P1 not active after spacebar"
        print("✓ Spacebar switches active player")

        # ── Pause disables switch button ────────────────────────────────
        await page.click("#pause-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("04_paused.png"))
        assert await page.text_content("#pause-btn") == "Resume",             "Expected 'Resume' when paused"
        assert await page.get_attribute("#switch-btn", "disabled") is not None, "Switch button should be disabled when paused"
        print("✓ Pause disables switch button")

        # ── Resume re-enables switch button ────────────────────────────
        await page.keyboard.press("Space")
        await page.wait_for_timeout(200)
        assert await page.text_content("#pause-btn") == "Pause",          "Expected 'Pause' after resume"
        assert await page.get_attribute("#switch-btn", "disabled") is None, "Switch button should be enabled after resume"
        print("✓ Resume re-enables switch button")

        # ── Game over: timed-out panel turns yellow ─────────────────────
        # Force P1's time close to zero via JS so we don't wait 5 minutes.
        await page.evaluate("state.times[0] = 500")
        await page.wait_for_timeout(800)
        await page.screenshot(path=shot("05_game_over.png"))

        p1_class = await page.get_attribute("#p1-panel", "class")
        p2_class = await page.get_attribute("#p2-panel", "class")
        assert "timed-out" in p1_class, f"P1 panel should have timed-out class, got: {p1_class}"
        assert "timed-out" not in p2_class, "P2 panel should not be timed-out"
        assert await page.get_attribute("#switch-btn", "disabled") is not None, "Switch should be disabled after game over"
        print("✓ Game over: losing panel gets timed-out class, switch button disabled")

        # ── New Game returns to setup with names pre-filled ─────────────
        await page.click("#new-game-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("06_new_game.png"))
        assert await page.is_visible("#setup-screen"),             "Setup screen not shown after New Game"
        assert await page.input_value("#p1-name-input") == "Dad", "P1 name not restored"
        assert await page.input_value("#p2-name-input") == "Kid", "P2 name not restored"
        print("✓ New Game → setup screen with names pre-filled")

        # ── Single Clock: time controls hidden, label + name fully visible ──
        await page.click("#btn-single-clock")
        await page.wait_for_timeout(200)

        # Time controls div must be hidden
        assert not await page.is_visible("#p2-time-controls"), "P2 time controls should be hidden in single-clock mode"
        # Label and name input must be fully visible and interactive
        assert await page.is_visible("#p2-name-input"), "P2 name input should be visible in single-clock mode"
        await page.fill("#p2-name-input", "TestKid")
        assert await page.input_value("#p2-name-input") == "TestKid", "P2 name input not editable in single-clock mode"
        await page.screenshot(path=shot("07_single_clock_setup.png"))
        print("✓ Single Clock: time controls hidden, P2 label and name input fully visible")

        await page.click("#start-btn")
        await page.wait_for_timeout(500)
        assert await page.text_content("#p2-time") == "—", "P2 should show '—' in single-clock mode"
        assert await page.text_content("#p2-name-display") == "TestKid", "P2 name should appear in game panel"
        await page.screenshot(path=shot("08_single_clock_game.png"))
        print("✓ Single Clock: P2 shows '—', custom name shown in panel")

        # NOTE: Timer color thresholds (warning at 2 min, critical at 1 min) are
        # not integration-tested here as they'd require waiting 1–2 minutes.
        # The constants WARNING_MS / CRITICAL_MS in app.js are the source of truth.

        await browser.close()
        server.shutdown()

    if errors:
        print(f"\n✗ JS errors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        raise SystemExit(1)
    else:
        print("\n✓ All checks passed, no JS errors")
        print(f"  Screenshots saved to screenshots/")

asyncio.run(run())
