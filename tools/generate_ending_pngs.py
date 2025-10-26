from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs(os.path.join('assets','ui'), exist_ok=True)

specs = [
    ('ending_1A.png', '#3b1f1f', '#e05b5b', 'Termination of Business (1A)', 'Placeholder artwork for Ending 1A'),
    ('ending_1B.png', '#3a3b1f', '#e0b85b', 'The Collapse of Idealism (1B)', 'Placeholder artwork for Ending 1B'),
    ('ending_apathy.png', '#303030', '#b8b8b8', 'The Art of Moderate Survival (Apathy)', 'Placeholder artwork for Apathy ending'),
    ('ending_best_red.png', '#1f4f36', '#8ee0b2', 'Integrity Preserved (Best Red)', 'Placeholder artwork for Best Red ending'),
]

W, H = 1280, 720

try:
    # try to load a TTF font from assets/fonts; fallback to default
    if os.path.exists(os.path.join('assets','fonts','m6x11plus.ttf')):
        title_font = ImageFont.truetype(os.path.join('assets','fonts','m6x11plus.ttf'), 56)
        body_font = ImageFont.truetype(os.path.join('assets','fonts','m6x11.ttf'), 28)
        note_font = ImageFont.truetype(os.path.join('assets','fonts','m6x11.ttf'), 20)
    else:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        note_font = ImageFont.load_default()
except Exception:
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    note_font = ImageFont.load_default()

for fname, rect_fill, stroke, title_text, body_text in specs:
    img = Image.new('RGB', (W, H), color=rect_fill)
    draw = ImageDraw.Draw(img)
    # outer framed rect
    margin = 40
    box = [margin, margin, W-margin, H-margin]
    # draw inner box with slight darker fill
    inner_fill = tuple(max(0, int(int(rect_fill.lstrip('#')[i:i+2],16)*0.9)) for i in (0,2,4)) if rect_fill.startswith('#') else (50,50,50)
    draw.rounded_rectangle(box, radius=20, fill=inner_fill, outline=stroke, width=6)

    # helper to compute text size across Pillow versions
    def _text_size(txt, fnt):
        try:
            return draw.textsize(txt, font=fnt)
        except Exception:
            try:
                return fnt.getsize(txt)
            except Exception:
                # fallback to textbbox
                bbox = draw.textbbox((0,0), txt, font=fnt)
                return (bbox[2]-bbox[0], bbox[3]-bbox[1])

    # title
    w, h = _text_size(title_text, title_font)
    draw.text(((W-w)/2, H*0.35 - h/2), title_text, font=title_font, fill=(255,255,255))
    # body
    wb, hb = _text_size(body_text, body_font)
    draw.text(((W-wb)/2, H*0.5 - hb/2), body_text, font=body_font, fill=(255,255,255))
    # note
    note = f'File: assets/ui/{fname} — replace with your final PNG when ready'
    wn, hn = _text_size(note, note_font)
    draw.text(((W-wn)/2, H*0.65 - hn/2), note, font=note_font, fill=(220,220,220))

    outp = os.path.join('assets','ui', fname)
    img.save(outp)
    print('Wrote', outp)

print('All placeholders generated.')
