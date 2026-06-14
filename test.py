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

        two_player  = await page.is_visible("#btn-two-player")
        single_clock = await page.is_visible("#btn-single-clock")
        print(f"  Mode buttons: Two Player={two_player}, Single Clock={single_clock}")

        presets  = await page.locator(".preset-btn").count()
        selected = await page.locator(".preset-btn.selected").all_text_contents()
        print(f"  Preset buttons: {presets}, pre-selected: {selected}")

        # ── Start game ──────────────────────────────────────────────────
        await page.click("#start-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("02_game_start.png"))
        print("✓ Game started")

        p1_start = await page.text_content("#p1-time")
        p2_start = await page.text_content("#p2-time")
        print(f"  Timers at start: P1={p1_start}, P2={p2_start}")

        # ── P1 clock counts down ────────────────────────────────────────
        await page.wait_for_timeout(2000)
        p1_after = await page.text_content("#p1-time")
        p1_class  = await page.get_attribute("#p1-panel", "class")
        print(f"  P1 after 2s: {p1_after}  (panel: {p1_class})")
        assert p1_after != p1_start, "P1 clock did not tick"
        assert "active" in p1_class, "P1 panel not highlighted"

        # ── Spacebar switches to P2 ─────────────────────────────────────
        await page.keyboard.press("Space")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("03_p2_active.png"))
        p1_class = await page.get_attribute("#p1-panel", "class")
        p2_class = await page.get_attribute("#p2-panel", "class")
        print(f"  After spacebar: P1={p1_class}, P2={p2_class}")
        assert "active" not in p1_class, "P1 still active after switch"
        assert "active" in p2_class, "P2 not active after switch"

        # ── P2 clock counts down ────────────────────────────────────────
        p2_before = await page.text_content("#p2-time")
        await page.wait_for_timeout(1100)
        p2_after  = await page.text_content("#p2-time")
        print(f"  P2 time: {p2_before} → {p2_after}")
        assert p2_after != p2_before, "P2 clock did not tick"

        # ── Pause / Resume ──────────────────────────────────────────────
        await page.click("#pause-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("04_paused.png"))
        btn_text = await page.text_content("#pause-btn")
        print(f"  Pause btn after click: '{btn_text}'")
        assert btn_text == "Resume", f"Expected 'Resume', got '{btn_text}'"

        await page.keyboard.press("Space")
        await page.wait_for_timeout(200)
        btn_text = await page.text_content("#pause-btn")
        print(f"  Pause btn after spacebar resume: '{btn_text}'")
        assert btn_text == "Pause", f"Expected 'Pause', got '{btn_text}'"

        # ── New Game returns to setup ────────────────────────────────────
        await page.click("#new-game-btn")
        await page.wait_for_timeout(300)
        await page.screenshot(path=shot("05_new_game.png"))
        assert await page.is_visible("#setup-screen"), "Setup screen not shown after New Game"
        print("✓ New Game → setup screen")

        # ── Single Clock mode ───────────────────────────────────────────
        await page.click("#btn-single-clock")
        await page.wait_for_timeout(200)
        p2_cfg = await page.get_attribute("#p2-config", "class")
        print(f"  P2 config class in single-clock: {p2_cfg}")
        assert "disabled" in p2_cfg, "P2 config not disabled in single-clock mode"
        await page.screenshot(path=shot("06_single_clock_setup.png"))

        await page.click("#start-btn")
        await page.wait_for_timeout(500)
        p2_display = await page.text_content("#p2-time")
        print(f"  P2 display in single-clock game: '{p2_display}'")
        assert p2_display == "—", f"Expected '—', got '{p2_display}'"
        await page.screenshot(path=shot("07_single_clock_game.png"))

        # ── Results ─────────────────────────────────────────────────────
        await browser.close()
        server.shutdown()

        if errors:
            print(f"\n✗ JS errors ({len(errors)}):")
            for e in errors:
                print(f"  {e}")
        else:
            print("\n✓ All checks passed, no JS errors")
            print(f"  Screenshots saved to screenshots/")

asyncio.run(run())
