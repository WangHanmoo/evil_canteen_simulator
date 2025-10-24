# Evil Canteen Simulator

A satirical, interactive Pygame project built for the course **Creative Programming for Designers and Artists**.

## Features
- Title menu (Start / Quit)
- Gameplay with core numeric system:
  - Evil value (0-10)
  - Complaints -> Warnings -> Closure
  - Inspector (bribe mechanic)
  - Time adjustments (per evil, idle bonuses)
- Multiple endings based on evil and warnings
- Clean separation between UI and logic (`gameplay_logic.py`)

## How to run
1. Install dependencies:
pip install -r requirements.txt
2. Run:
python main.py

## Placeholder UI images (for quick testing)

This project uses placeholder image filenames in `assets/ui/` so you can drop in your own art later. I generated simple PNG placeholders in the repo so the game will display something by default.

Recommended filenames and suggested sizes/styles:

- `PICTURE_background.png` — 1280×720, a subtle textured background, low contrast so UI pops.
- `PICTURE_figure.png` — 300×300, decorative character / mascot, left side of title screen.
- `PICTURE_button1.png`, `PICTURE_button2.png` — 360×64 or similar, button art; keep readable text area in center.
- `PICTURE_text box.png` — 800×200, large dialog/event box background; semi-transparent dark panel works well.

Style notes:
- Use clear, high-contrast text areas; avoid busy patterns where UI text appears.
- Keep art assets slightly larger than target sizes so the game can downscale smoothly.
- Place assets in `assets/ui/` and keep filenames as above to have the game automatically pick them up.

If you want, I can also create template PSD/SVG layout guides with safe areas for text/buttons.

