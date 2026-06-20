#!/usr/bin/env python3
"""Record a real screen-capture promo video of Mahdiesta Arsenal interactions."""
import os
import subprocess
import time
from playwright.sync_api import sync_playwright

PROJECT = "/home/kali/mahdiesta/TheCompleteMahdiestaArsenal"
SHOTS_DIR = os.path.join(PROJECT, "video_shots")
os.makedirs(SHOTS_DIR, exist_ok=True)

RAW_VIDEO = os.path.join(SHOTS_DIR, "raw-screen-recording.webm")
BASE_URL = "http://localhost:8000"

# MacBook screen area
SCREEN_W, SCREEN_H = 1770, 930


def start_server():
    subprocess.run(["pkill", "-f", "http.server 8000"], capture_output=True)
    time.sleep(0.5)
    proc = subprocess.Popen(
        ["python3", "-m", "http.server", "8000"],
        cwd=PROJECT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    return proc


def record():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": SCREEN_W, "height": SCREEN_H},
            record_video_dir=SHOTS_DIR,
            record_video_size={"width": SCREEN_W, "height": SCREEN_H},
        )
        page = context.new_page()

        def goto(path):
            page.goto(f"{BASE_URL}/{path}", wait_until="networkidle")

        # 1. Landing page
        goto("index.html")
        page.evaluate("window.scrollTo(0,0)")
        time.sleep(4.0)

        # 2. Search shortcut + type mimikatz
        page.keyboard.press("/")
        time.sleep(0.4)
        page.keyboard.type("mimikatz", delay=70)
        time.sleep(2.5)

        # 3. Clear search and cycle category filters
        page.keyboard.press("Escape")
        time.sleep(0.5)

        page.click("button[data-filter='ad']")
        time.sleep(2.0)
        page.click("button[data-filter='sql']")
        time.sleep(1.8)
        page.click("button[data-filter='web']")
        time.sleep(1.8)
        page.click("button[data-filter='all']")
        time.sleep(1.2)

        # 4. Open ADCS sheet
        goto("adcs-arsenal.html")
        time.sleep(2.5)

        # 5. Edit a target variable (DC_IP) - commands auto-update
        page.click("#v_DC_IP")
        page.keyboard.press("Control+a")
        page.keyboard.type("192.168.1.10", delay=40)
        time.sleep(1.2)

        # 6. Scroll to a command and click Copy
        page.evaluate("window.scrollTo(0, 420)")
        time.sleep(0.6)
        page.click(".cmd-copy-btn")
        time.sleep(2.0)

        # 7. Toggle theme with T
        page.keyboard.press("t")
        time.sleep(3.0)

        # 8. Open SQLi → RCE sheet
        goto("sqli-rce.html")
        time.sleep(2.5)

        # 9. Scroll to a payload and copy
        page.evaluate("window.scrollTo(0, 420)")
        time.sleep(0.6)
        page.locator(".copy-btn").first.click()
        time.sleep(2.0)

        # 10. Back to index and show keyboard shortcuts with ?
        goto("index.html")
        time.sleep(1.5)
        page.keyboard.press("?")
        time.sleep(3.0)
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 11. Outro scroll to footer
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(4.0)

        context.close()
        browser.close()

        videos = [
            os.path.join(SHOTS_DIR, f)
            for f in os.listdir(SHOTS_DIR)
            if f.endswith(".webm")
        ]
        if not videos:
            raise RuntimeError("No video was recorded")
        latest = max(videos, key=os.path.getmtime)
        os.replace(latest, RAW_VIDEO)
        print(f"Screen recording saved to: {RAW_VIDEO}")


if __name__ == "__main__":
    server = start_server()
    try:
        record()
    finally:
        server.terminate()
