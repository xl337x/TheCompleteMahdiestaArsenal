#!/usr/bin/env python3
"""Assemble the Mahdiesta Arsenal promo video from screenshots."""
import os
from moviepy import (
    ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
)
from moviepy.video.fx import Resize

PROJECT = "/home/kali/mahdiesta/TheCompleteMahdiestaArsenal"
SHOTS_DIR = os.path.join(PROJECT, "video_shots")
FRAME_PATH = os.path.join(PROJECT, "macbook-frame.png")
OUTPUT = os.path.join(PROJECT, "mahdiesta-arsenal-promo.mp4")

# Video specs
W, H = 1920, 1080
FPS = 30

# Shot definitions: (image, duration, caption, effect)
SHOTS = [
    ("01_intro.png", 5, "Tired of scattered cheat sheets?", "zoom-in"),
    ("02_filters.png", 4, "Meet Mahdiesta Arsenal — 14 interactive sheets.", "pan-down"),
    ("03_search.png", 4, "Search any tool, technique, or command.", "none"),
    ("04_filter_ad.png", 2, "Active Directory", "none"),
    ("05_filter_sql.png", 2, "SQL Injection", "none"),
    ("06_filter_web.png", 2, "Web Exploitation", "none"),
    ("07_filter_privesc.png", 2, "Privilege Escalation", "none"),
    ("08_adcs.png", 5, "Copyable commands + variable auto-fill.", "zoom-in"),
    ("09_adcs_light.png", 3, "Dark / light mode with one key.", "none"),
    ("10_sqli_rce.png", 5, "SQLi to RCE, web enum, auth bypass.", "pan-down"),
    ("11_outro.png", 6, "Open source. Free. Link in comments.", "none"),
]

def apply_effect(clip, effect, duration):
    if effect == "zoom-in":
        # Ken Burns zoom from 1.0 to 1.08 over the duration
        def resize_func(t):
            return 1.0 + 0.08 * (t / duration)
        return clip.with_effects([Resize(resize_func)])
    elif effect == "pan-down":
        # Start at y offset -60, end at 0 (relative to center)
        def position_func(t):
            progress = t / duration
            y = -60 * (1 - progress)
            return ("center", y)
        return clip.with_position(position_func)
    return clip

def create_shot(image, duration, caption, effect):
    img_path = os.path.join(SHOTS_DIR, image)
    clip = ImageClip(img_path).with_duration(duration)

    # Scale screenshot to fit inside MacBook screen area
    target_w, target_h = 1740, 1040
    clip = clip.with_effects([Resize(new_size=(target_w, target_h))])
    clip = clip.with_position(("center", "center"))

    # Apply subtle motion effect
    clip = apply_effect(clip, effect, duration)

    # Caption
    txt = TextClip(
        text=caption,
        font="/usr/share/fonts/truetype/lato/Lato-Bold.ttf",
        font_size=42,
        color="white",
        stroke_color="black",
        stroke_width=2,
        method="caption",
        size=(W - 200, None),
        text_align="center"
    ).with_duration(duration).with_position(("center", H - 140))

    # Frame overlay
    frame = ImageClip(FRAME_PATH).with_duration(duration)
    frame = frame.with_effects([Resize(new_size=(W, H))])

    return CompositeVideoClip([clip, frame, txt], size=(W, H)).with_duration(duration)

def main():
    clips = []
    for image, duration, caption, effect in SHOTS:
        print(f"Processing {image}...")
        clips.append(create_shot(image, duration, caption, effect))

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        OUTPUT,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        threads=4
    )
    print(f"\nVideo saved to: {OUTPUT}")

if __name__ == "__main__":
    main()
