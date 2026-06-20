#!/usr/bin/env python3
"""Generate a MacBook-style frame PNG with a transparent screen cutout."""
from PIL import Image, ImageDraw

W, H = 1920, 1080

# Frame dimensions
bezel_top = 60
bezel_bottom = 90
bezel_sides = 75
screen_x = bezel_sides
screen_y = bezel_top
screen_w = W - 2 * bezel_sides
screen_h = H - bezel_top - bezel_bottom
radius = 24

# Create transparent image
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Laptop body (dark aluminum/black)
body_color = (18, 18, 20, 255)
# Top lid rounded rectangle
draw.rounded_rectangle([0, 0, W-1, H-1-bezel_bottom//2], radius=radius, fill=body_color)
# Bottom base (slightly wider) - simple rounded rect at bottom
base_y = H - bezel_bottom
base_height = 40
draw.rounded_rectangle([0, base_y, W-1, H-1], radius=12, fill=body_color)

# Screen cutout (transparent)
draw.rounded_rectangle(
    [screen_x, screen_y, screen_x + screen_w - 1, screen_y + screen_h - 1],
    radius=12,
    fill=(0, 0, 0, 0)
)

# Camera notch / little dot at top center
notch_w, notch_h = 12, 12
notch_x = W // 2 - notch_w // 2
notch_y = 22
draw.ellipse([notch_x, notch_y, notch_x + notch_w - 1, notch_y + notch_h - 1], fill=(60, 60, 65, 255))

# Trackpad hint on base
tp_w, tp_h = 160, 18
tp_x = W // 2 - tp_w // 2
tp_y = H - 28
draw.rounded_rectangle([tp_x, tp_y, tp_x + tp_w - 1, tp_y + tp_h - 1], radius=8, fill=(45, 45, 50, 255))

# Subtle inner bezel highlight (very thin line around screen)
draw.rounded_rectangle(
    [screen_x, screen_y, screen_x + screen_w - 1, screen_y + screen_h - 1],
    radius=12,
    outline=(50, 50, 55, 255),
    width=2
)

img.save("macbook-frame.png")
print("Saved macbook-frame.png")
