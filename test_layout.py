#!/usr/bin/env python3
"""
Mobile layout assertions for the chess timer.

Checks that on real phone viewport sizes:
  - The knight button does not obscure timer or player-name content in either panel
  - The controls bar is not clipped by the bottom of the viewport
  - The P1 timer clears the simulated status-bar threshold (60px, the CSS fallback)

Run from the project root:  python3 test_layout.py
Screenshots land in screenshots/layout_<device>.png for inspection.
"""

import asyncio
import os
import threading
import http.server
import functools
from playwright.async_api import async_playwright

PORT = 7823
SCREENSHOTS = os.path.join(os.path.dirname(__file__), "screenshots")

# Portrait viewports for common iPhones
DEVICES = [
    {"name": "iphone-se-3rd",    "width": 375, "height": 667},
    {"name": "iphone-14",        "width": 390, "height": 844},
    {"name": "iphone-14-pro-max","width": 430, "height": 932},
]

# env(safe-area-inset-top) returns 0 in headless Chromium, so the CSS
# max(env(...), 60px) resolves to 60px — that is the threshold we validate.
STATUS_BAR_THRESHOLD = 60


def overlaps(a, b):
    """True if two bounding-box dicts share any pixels."""
    return not (
        a["x"] + a["width"]  <= b["x"] or
        b["x"] + b["width"]  <= a["x"] or
        a["y"] + a["height"] <= b["y"] or
        b["y"] + b["height"] <= a["y"]
    )


def start_server():
    os.makedirs(SCREENSHOTS, exist_ok=True)
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=os.path.dirname(__file__),
    )
    server = http.server.HTTPServer(("", PORT), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


async def check_device(page, device):
    await page.set_viewport_size({"width": device["width"], "height": device["height"]})
    await page.goto(f"http://localhost:{PORT}/")
    await page.wait_for_load_state("networkidle")
    await page.click("#start-btn")
    await page.wait_for_timeout(300)  # let CSS settle

    shot = os.path.join(SCREENSHOTS, f"layout_{device['name']}.png")
    await page.screenshot(path=shot)

    btn  = await page.locator("#switch-btn").bounding_box()
    p1t  = await page.locator("#p1-time").bounding_box()
    p2t  = await page.locator("#p2-time").bounding_box()
    p1n  = await page.locator("#p1-name-display").bounding_box()
    p2n  = await page.locator("#p2-name-display").bounding_box()
    bar  = await page.locator(".controls-bar").bounding_box()
    vp   = page.viewport_size

    p1_panel = await page.locator("#p1-panel").bounding_box()
    p2_panel = await page.locator("#p2-panel").bounding_box()
    p1_piece = await page.locator("#p1-panel .player-piece").bounding_box()

    failures = []

    # Button must be centred on the p1/p2 boundary (within 2px).
    panel_boundary_y = p1_panel["y"] + p1_panel["height"]
    btn_center_y = btn["y"] + btn["height"] / 2
    if abs(btn_center_y - panel_boundary_y) > 2:
        failures.append(
            f"Knight button not centred on panel boundary: "
            f"btn_center_y={btn_center_y:.1f}  boundary_y={panel_boundary_y:.1f}"
        )

    if overlaps(p1t, btn):
        failures.append(
            f"P1 timer overlaps knight button  "
            f"timer=[{p1t['y']:.0f}–{p1t['y']+p1t['height']:.0f}]  "
            f"btn=[{btn['y']:.0f}–{btn['y']+btn['height']:.0f}]  "
            f"(panel={p1_panel['height']:.0f}px  piece={p1_piece['height']:.0f}px  "
            f"name={p1n['height']:.0f}px  timer={p1t['height']:.0f}px)"
        )
    if overlaps(p2t, btn):
        failures.append(
            f"P2 timer overlaps knight button  "
            f"timer=[{p2t['y']:.0f}–{p2t['y']+p2t['height']:.0f}]  "
            f"btn=[{btn['y']:.0f}–{btn['y']+btn['height']:.0f}]"
        )
    if overlaps(p1n, btn):
        failures.append(f"P1 name overlaps knight button")
    if overlaps(p2n, btn):
        failures.append(f"P2 name overlaps knight button")

    bar_bottom = bar["y"] + bar["height"]
    if bar_bottom > vp["height"]:
        failures.append(
            f"Controls bar clipped: bar bottom={bar_bottom:.0f} > viewport={vp['height']}"
        )

    if p1t["y"] < STATUS_BAR_THRESHOLD:
        failures.append(
            f"P1 timer too close to top (status bar risk): "
            f"y={p1t['y']:.0f} < threshold={STATUS_BAR_THRESHOLD}"
        )

    return failures, shot


async def run():
    server = start_server()
    any_failure = False

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for device in DEVICES:
            label = f"{device['name']} ({device['width']}×{device['height']})"
            page = await browser.new_page()
            failures, shot = await check_device(page, device)
            await page.close()

            if failures:
                any_failure = True
                print(f"✗ {label}")
                for f in failures:
                    print(f"    {f}")
            else:
                print(f"✓ {label}")
            print(f"    screenshot: {shot}")

        await browser.close()
        server.shutdown()

    if any_failure:
        raise SystemExit(1)
    else:
        print("\n✓ All layout checks passed")


asyncio.run(run())
