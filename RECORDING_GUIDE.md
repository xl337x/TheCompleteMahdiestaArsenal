# How to Record the LinkedIn Video (MacBook Look)

## Tools Needed
- **OBS Studio** (free, Linux/Windows/Mac)
- **macbook-frame.png** from this folder
- A video editor: DaVinci Resolve (free) or Canva

---

## Step 1: Prepare the Scene

1. Open Chrome and go to `http://localhost:8000/index.html`
2. Resize Chrome window to **1728×1117** pixels.
   - On Linux: `wmctrl -r "Chrome" -e 0,0,0,1728,1117`
3. Hide bookmarks bar and dev tools for clean look.
4. Set system wallpaper to a clean dark gradient.

---

## Step 2: Record with OBS

1. Open OBS → Settings → Video → Base/Output Resolution: **1920×1080**
2. Add a **Browser** source or **Window Capture** source pointing to Chrome
3. Position the browser window in the center
4. Add the **macbook-frame.png** as an Image source on top
5. Scale the frame so the screen cutout matches your browser window
6. Start Recording → follow the `VIDEO_SCRIPT.md` timing
7. Stop Recording

---

## Step 3: Edit (DaVinci Resolve or Canva)

1. Import the OBS recording
2. Add the `VIDEO_SCRIPT.md` captions at each timestamp
3. Add background music (low volume)
4. Add the final CTA screen: "Mahdiesta Arsenal — link in comments"
5. Export as MP4, 1080p, 30fps

---

## Step 4: Post on LinkedIn

1. Upload the MP4
2. Add caption from `VIDEO_SCRIPT.md`
3. Use hashtags:
   - #CyberSecurity
   - #OffensiveSecurity
   - #RedTeam
   - #PenetrationTesting
   - #GitHub
   - #OpenSource

---

## Pro Tips
- Record at 60fps if your hardware supports it (smoother mouse movement)
- Use a 16:9 output for LinkedIn feed, or 9:16 if posting as a Reel/Story
- Keep captions on screen for at least 3 seconds
