import os
import sys
import random
import pygame

# Simple self-contained game implementing the four scenes described by the user.
# Uses placeholder image names like 'PICTURE_button1.png' etc. Fonts: m6x11.ttf, m6x11plus.ttf

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 60


def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.SysFont("arial", size)


def load_image(path, size=None):
    """Try to load an image; if missing, return a placeholder surface with the filename text."""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        w, h = size if size else (200, 80)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((80, 80, 80))
        # draw a simple label
        try:
            f = pygame.font.SysFont("arial", 14)
            txt = f.render(os.path.basename(path), True, (230, 230, 230))
            surf.blit(txt, (6, 6))
        except Exception:
            pass
        return surf


def wrap_text(text, font, max_width):
    """Simple word-wrap: return list of lines that fit within max_width using font.size()."""
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            # if single word longer than max_width, force-break
            if font.size(w)[0] > max_width:
                # break the word into characters
                part = ''
                for ch in w:
                    if font.size(part + ch)[0] <= max_width:
                        part += ch
                    else:
                        if part:
                            lines.append(part)
                        part = ch
                if part:
                    cur = part
                else:
                    cur = ''
            else:
                cur = w
    if cur:
        lines.append(cur)
    return lines


# --- Sound helper -------------------------------------------------
class SoundManager:
    def __init__(self):
        self.available = False
        self.click = None
        self.select = None
        self.bgm_path = None
        try:
            # initialize mixer with reasonable defaults; ignore failures
            pygame.mixer.init(frequency=44100)
            self.available = True
        except Exception:
            print("[SoundManager] audio mixer unavailable; continuing without sound")
            self.available = False
            return

        # try load common sfx names from assets/sounds
        sfx_dir = os.path.join('assets', 'sounds')
        try:
            click_candidates = ['click.wav', 'click.ogg', 'select.wav', 'select.ogg']
            for fn in click_candidates:
                p = os.path.join(sfx_dir, fn)
                if os.path.exists(p):
                    try:
                        self.click = pygame.mixer.Sound(p)
                        break
                    except Exception:
                        self.click = None
            # fallback: look for any file starting with 'click' or 'select'
            if not self.click and os.path.isdir(sfx_dir):
                for fn in os.listdir(sfx_dir):
                    if fn.lower().startswith('click') or fn.lower().startswith('select'):
                        p = os.path.join(sfx_dir, fn)
                        try:
                            self.click = pygame.mixer.Sound(p)
                            break
                        except Exception:
                            continue

            # optional select sound (alias)
            sel_candidates = ['select.wav', 'select.ogg']
            for fn in sel_candidates:
                p = os.path.join(sfx_dir, fn)
                if os.path.exists(p):
                    try:
                        self.select = pygame.mixer.Sound(p)
                        break
                    except Exception:
                        self.select = None

            # background music: try common names
            for name in ('bgm.ogg', 'bgm.mp3', 'bgm.wav', 'music.ogg', 'music.mp3'):
                p = os.path.join(sfx_dir, name)
                if os.path.exists(p):
                    try:
                        self.bgm_path = p
                        break
                    except Exception:
                        self.bgm_path = None
        except Exception:
            pass

    def play_click(self):
        try:
            if not self.available:
                return
            if self.click:
                self.click.play()
        except Exception:
            pass

    def play_select(self):
        try:
            if not self.available:
                return
            if self.select:
                self.select.play()
            elif self.click:
                self.click.play()
        except Exception:
            pass

    def play_bgm(self, loop=True):
        try:
            if not self.available or not self.bgm_path:
                return
            # use mixer.music for streaming bgm
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.play(-1 if loop else 0)
            except Exception:
                pass
        except Exception:
            pass

    def stop_bgm(self):
        try:
            if not self.available:
                return
            pygame.mixer.music.stop()
        except Exception:
            pass


class Button:
    def __init__(self, rect, text, font, color=(100, 50, 140), hover=(240, 200, 60)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color = color
        self.hover = hover

    def draw(self, surf):
        mpos = pygame.mouse.get_pos()
        c = self.hover if self.rect.collidepoint(mpos) else self.color
        pygame.draw.rect(surf, c, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class AnimatedButton(Button):
    """Button with simple hover/press scale animation for interactive feel."""
    def __init__(self, rect, text, font, color=(100,50,140), hover=(240,200,60), bg_image=None):
        super().__init__(rect, text, font, color=color, hover=hover)
        self.scale = 1.0
        self.target_scale = 1.0
        self.pressed = False
        # optional background image Surface (original, not scaled). If provided, it will be
        # scaled each frame to the drawn rect size for crisp rendering.
        self.bg_image = bg_image

    def draw(self, surf):
        mpos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mpos)
        if hovered:
            self.target_scale = 1.08
        else:
            self.target_scale = 1.0

        # smooth approach to target scale
        if self.scale < self.target_scale:
            self.scale = min(self.scale + 0.06, self.target_scale)
        elif self.scale > self.target_scale:
            self.scale = max(self.scale - 0.06, self.target_scale)

        # compute scaled rect centered on original rect center
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        cx, cy = self.rect.center
        draw_rect = pygame.Rect(0,0,w,h)
        draw_rect.center = (cx, cy)

        if getattr(self, 'bg_image', None):
            try:
                bi = pygame.transform.smoothscale(self.bg_image, (draw_rect.width, draw_rect.height))
                surf.blit(bi, draw_rect.topleft)
            except Exception:
                # fallback to colored rect if image blit/scale fails
                c = self.hover if hovered else self.color
                pygame.draw.rect(surf, c, draw_rect, border_radius=8)
        else:
            c = self.hover if hovered else self.color
            pygame.draw.rect(surf, c, draw_rect, border_radius=8)

        # option text color set to #b90c0c per request
        txt = self.font.render(self.text, True, (185,12,12))
        surf.blit(txt, txt.get_rect(center=draw_rect.center))

    def handle_event(self, event):
        # keep the simple click detection but allow for scaled rect
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # map event.pos into scaled rect space
            w = int(self.rect.width * self.scale)
            h = int(self.rect.height * self.scale)
            cx, cy = self.rect.center
            draw_rect = pygame.Rect(0,0,w,h)
            draw_rect.center = (cx, cy)
            if draw_rect.collidepoint(event.pos):
                self.pressed = True
                return True
        return False


class HeartBar:
    def __init__(self, max_hearts=10, images=None):
        self.max = max_hearts
        # images: dict with keys 'red','grey','black','empty' holding pygame Surfaces
        self.images = images or {}

    def draw(self, surf, value, x=None, y=None, size=16, spacing=20):
        """Draw hearts horizontally. If x/y provided, draw starting there (left->right).
        Otherwise default to top-right (draws right-to-left).
        """
        if x is None:
            # right-to-left starting from near right edge
            x0 = WINDOW_WIDTH - 20 - size
            y0 = 20
            for i in range(self.max):
                xi = x0 - i * spacing
                yi = y0
                if i < value:
                    if value >= 8:
                        img = self.images.get('red')
                    elif value >= 4:
                        img = self.images.get('grey')
                    else:
                        img = self.images.get('black')
                else:
                    img = self.images.get('empty')
                    is_empty = (i >= value)
                    if img:
                        try:
                            img_s = pygame.transform.smoothscale(img, (size, size))
                            surf.blit(img_s, (xi, yi))
                        except Exception:
                            # if scaling/blit fails, draw a simple polygon placeholder for full hearts
                            if not is_empty:
                                pygame.draw.polygon(surf, (120, 120, 120), [(xi, yi + 6), (xi + int(size/2), yi), (xi + size, yi + 6), (xi + int(size/2), yi + size + 6)])
                    else:
                        # If empty-heart sprite is missing, don't draw the placeholder 'fourth' shape;
                        # leave empty space. For missing full-heart sprites we still draw a polygon.
                        if not is_empty:
                            pygame.draw.polygon(surf, (120, 120, 120), [(xi, yi + 6), (xi + int(size/2), yi), (xi + size, yi + 6), (xi + int(size/2), yi + size + 6)])
        else:
            # left-to-right inside a given panel
            for i in range(self.max):
                xi = x + i * spacing
                yi = y
                if i < value:
                    if value >= 8:
                        img = self.images.get('red')
                    elif value >= 4:
                        img = self.images.get('grey')
                    else:
                        img = self.images.get('black')
                else:
                    img = self.images.get('empty')
                is_empty = (i >= value)
                if img:
                    try:
                        img_s = pygame.transform.smoothscale(img, (size, size))
                        surf.blit(img_s, (xi, yi))
                    except Exception:
                        if not is_empty:
                            pygame.draw.polygon(surf, (120, 120, 120), [(xi, yi + 6), (xi + int(size/2), yi), (xi + size, yi + 6), (xi + int(size/2), yi + size + 6)])
                else:
                    if not is_empty:
                        pygame.draw.polygon(surf, (120, 120, 120), [(xi, yi + 6), (xi + int(size/2), yi), (xi + size, yi + 6), (xi + int(size/2), yi + size + 6)])

    def update(self, dt):
        pass

    def render(self, surf):
        pass


class SceneBase:
    def __init__(self, game):
        self.game = game

    def start(self):
        pass

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def render(self, surf):
        pass


class TitleScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 64)
        # increase button font size for better visibility on title screen
        self.btn_font = load_font("assets/fonts/m6x11.ttf", 40)
        # use the JPG background for the title screen explicitly
        self.bg = load_image(os.path.join('assets', 'ui', 'PICTURE_background.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
        # change Start/Quit button base color to #e5002b
        btn_color = (229, 0, 43)
        btn_hover = (255, 60, 80)
        # button rects
        start_rect = (WINDOW_WIDTH//2-180, 360, 360, 64)
        quit_rect = (WINDOW_WIDTH//2-180, 440, 360, 64)
        self.start_btn = Button(start_rect, "Start Game", self.btn_font, color=btn_color, hover=btn_hover)
        self.quit_btn = Button(quit_rect, "Quit", self.btn_font, color=btn_color, hover=btn_hover)

        # try to use textured button images for the title screen (A for Start, B for Quit)
        try:
            bpa = os.path.join('assets', 'ui', 'button_cA.png')
            bpb = os.path.join('assets', 'ui', 'button_cB.png')
            self.start_img = load_image(bpa, (self.start_btn.rect.width, self.start_btn.rect.height)) if os.path.exists(bpa) else None
            self.quit_img = load_image(bpb, (self.quit_btn.rect.width, self.quit_btn.rect.height)) if os.path.exists(bpb) else None
        except Exception:
            self.start_img = None
            self.quit_img = None

    def handle_events(self, events):
        for e in events:
            if self.start_btn.handle_event(e):
                try:
                    # play click SFX if available
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                self.game.start_new_run()
            if self.quit_btn.handle_event(e):
                try:
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                pygame.quit(); sys.exit()

    def render(self, surf):
        # Prefer a final ending image if the artist provided one. Filenames mapped below.
        # Use the project-wide mapping so keys map to the filenames you provided.
        ending_map = {
            'spiral': 'ending_spiral.png',
            '1A': 'ending_1A.png',
            'best_red': 'ending_1B.png',
            'apathy': 'ending_apathy.png',
        }
        png_name = ending_map.get(getattr(self, 'key', None))
        if png_name:
            png_path = os.path.join('assets', 'ui', png_name)
            if os.path.exists(png_path):
                try:
                    # cache the loaded full-screen image on the scene instance so we don't reload every frame
                    if not hasattr(self, '_cached_ending_img') or getattr(self, '_cached_ending_img_path', None) != png_path:
                        print(f"[EndingScene] Loading ending image: {png_path}")
                        self._cached_ending_img = load_image(png_path, (WINDOW_WIDTH, WINDOW_HEIGHT))
                        self._cached_ending_img_path = png_path
                    img = self._cached_ending_img
                    surf.blit(img, (0, 0))
                    return
                except Exception as ex:
                    print(f"[EndingScene] Failed to load ending image {png_path}: {ex}")
                    # fall back to existing text rendering
                    pass

        # fallback: draw background (plain or provided)
        surf.blit(self.bg, (0,0))
        # draw Start/Quit using textured images if available, otherwise fallback to button draw
        if getattr(self, 'start_img', None):
            surf.blit(self.start_img, self.start_btn.rect.topleft)
            # draw label on top with requested color #b90c0c
            txt = self.btn_font.render(self.start_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.start_btn.rect.center))
        else:
            # fallback draw then overdraw label with requested color to ensure visibility
            self.start_btn.draw(surf)
            txt = self.btn_font.render(self.start_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.start_btn.rect.center))

        if getattr(self, 'quit_img', None):
            surf.blit(self.quit_img, self.quit_btn.rect.topleft)
            txt = self.btn_font.render(self.quit_btn.text, True, (255,255,255))
            surf.blit(txt, txt.get_rect(center=self.quit_btn.rect.center))
        else:
            # fallback draw; keep quit label white
            self.quit_btn.draw(surf)
            txt = self.btn_font.render(self.quit_btn.text, True, (255,255,255))
            surf.blit(txt, txt.get_rect(center=self.quit_btn.rect.center))


class PrepScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 26)
        # title font for centered stage heading
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 48)
        # prepare 2x2 grid centered with animated interactive buttons
        btn_w = 420
        btn_h = 110
        spacing = 36
        # (text, heart_delta, money_delta)
        self.options = [
            ("Use expired ingredients (-2)", -2, +50),
            ("Ignore insect bodies (-1)", -1, +30),
            ("Ignore dirty utensils (-1)", -1, +20),
            ("Clean thoroughly (+0)", 0, -80),
        ]
        self.buttons = []
        grid_w = btn_w * 2 + spacing
        grid_h = btn_h * 2 + spacing
        start_x = (WINDOW_WIDTH - grid_w) // 2
        start_y = (WINDOW_HEIGHT - grid_h) // 2
        # try to use a provided button art for prep options
        try:
            prep_btn_path = os.path.join('assets', 'ui', 'PICTURE_button1.png')
            prep_btn_img = load_image(prep_btn_path) if os.path.exists(prep_btn_path) else None
        except Exception:
            prep_btn_img = None

        for idx, (t, v, m) in enumerate(self.options):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (btn_w + spacing)
            y = start_y + row * (btn_h + spacing)
            rect = (x, y, btn_w, btn_h)
            self.buttons.append(AnimatedButton(rect, t, self.font, color=(100,50,140), hover=(240,200,60), bg_image=prep_btn_img))

        # instruction modal before any choice
        self.show_instruction = True
        self.instruction_text = (
            "Preparation phase: choose how you prepare the food.\n"
            "Each choice changes Integrity (hearts) and Money.\n"
            "Click anywhere to continue and make your selection."
        )
        # typewriter effect state
        self.instruction_progress = 0.0  # float to accumulate chars/sec
        self.instruction_speed = 120.0  # chars per second
        # prefer background image for prep scene from assets/ui/background.png
        try:
            bg_path = os.path.join('assets', 'ui', 'background.png')
            self.bg = load_image(bg_path, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception:
            self.bg = None

    def handle_events(self, events):
        # if instruction modal visible, consume clicks to dismiss only
        for e in events:
            if self.show_instruction:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # if typing still in progress, complete immediately; otherwise dismiss
                    if int(self.instruction_progress) < len(self.instruction_text):
                        self.instruction_progress = float(len(self.instruction_text))
                    else:
                        try:
                            if getattr(self.game, 'sound', None):
                                self.game.sound.play_click()
                        except Exception:
                            pass
                        self.show_instruction = False
                continue

            for i, btn in enumerate(self.buttons):
                if btn.handle_event(e):
                    try:
                        if getattr(self.game, 'sound', None):
                            self.game.sound.play_click()
                    except Exception:
                        pass
                    heart_delta = self.options[i][1]
                    money_delta = self.options[i][2]
                    self.game.change_hearts(heart_delta)
                    self.game.change_money(money_delta)
                    self.game.add_log(f"Prep choice: {self.options[i][0]} (money {money_delta:+d})")
                    # proceed to business after a choice
                    self.game.change_scene('business')

    def render(self, surf):
        # draw scene background (prefer provided background.png)
        try:
            if getattr(self, 'bg', None):
                surf.blit(self.bg, (0, 0))
            else:
                surf.fill((30, 30, 30))
        except Exception:
            surf.fill((30, 30, 30))
        # centered, larger stage title with pink outline (#fd69fd)
        title_text = 'Preparation Phase'
        title_pos = (WINDOW_WIDTH//2, 140)
        pink = (253, 105, 253)
        # draw simple outline by stamping the pink text slightly offset in four directions
        outline_s = self.title_font.render(title_text, True, pink)
        for ox, oy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            surf.blit(outline_s, outline_s.get_rect(center=(title_pos[0] + ox, title_pos[1] + oy)))
        title_s = self.title_font.render(title_text, True, (185,12,12))
        surf.blit(title_s, title_s.get_rect(center=title_pos))
        # keep focus on four-grid buttons
        for b in self.buttons:
            b.draw(surf)
        # draw instruction modal on top if needed (typewriter effect)
        if getattr(self, 'show_instruction', False):
            # dim the underlying scene so the modal becomes the primary focus
            try:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                surf.blit(overlay, (0, 0))
            except Exception:
                pass

            box_w, box_h = 760, 160
            bx = (WINDOW_WIDTH - box_w)//2
            by = (WINDOW_HEIGHT - box_h)//2
            panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            # instruction modal color: #64d591 with 80% opacity (alpha=204)
            panel.fill((100, 213, 145, 204))
            # pink outline #fd69fd for the panel border
            pygame.draw.rect(panel, (253,105,253), (0,0,box_w,box_h), width=2, border_radius=8)
            f = load_font("assets/fonts/m6x11.ttf", 24)
            # compute visible text according to progress
            visible = self.instruction_text[:int(self.instruction_progress)]
            lines = visible.split('\n')
            for i, ln in enumerate(lines):
                panel.blit(f.render(ln, True, (240,240,240)), (18, 18 + i*28))
            hint = f.render('Click to continue', True, (200,200,200))
            panel.blit(hint, (box_w - hint.get_width() - 12, box_h - hint.get_height() - 12))
            surf.blit(panel, (bx, by))

    def update(self, dt):
        # advance typewriter for instruction modal
        if getattr(self, 'show_instruction', False) and int(self.instruction_progress) < len(self.instruction_text):
            self.instruction_progress += (dt * self.instruction_speed) / 1000.0
            if self.instruction_progress > len(self.instruction_text):
                self.instruction_progress = float(len(self.instruction_text))


class BusinessScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        # larger fonts for business phase
        self.font = load_font("assets/fonts/m6x11.ttf", 28)
        # centered title font
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 44)
        # (text, heart_delta, money_delta)
        self.action_opts = [
            ("Do nothing about cockroaches [*5]", -1, +30),
            ("Use dirty plates [*5]", -1, +40),
            ("Give students very small portions [*5]", -1, +20),
            ("Serve wrong dish [*5]", 0, -10),
            # New option: occupies a full row under the original four, same effect as Serve wrong dish
            ("Serving hearty and delicious dishes [*5]", 0, -10),
        ]
        # create centered 2x2 grid of animated buttons (same style as PrepScene)
        self.buttons = []
        btn_w = 420
        btn_h = 110
        spacing = 36
        # dynamic rows: two columns layout, last odd item will occupy full width
        cols = 2
        rows = (len(self.action_opts) + cols - 1) // cols
        grid_w = btn_w * cols + spacing
        grid_h = btn_h * rows + spacing * (rows - 1)
        start_x = (WINDOW_WIDTH - grid_w) // 2
        # previously shifted down by 90px; move the block up by 50px from that position => +40
        start_y = (WINDOW_HEIGHT - grid_h) // 2 + 40
        # load per-option button art: first four use PICTURE_button2.png, last (long) uses PICTURE_button3.png
        try:
            pic2_path = os.path.join('assets', 'ui', 'PICTURE_button2.png')
            pic3_path = os.path.join('assets', 'ui', 'PICTURE_button3.png')
            pic2 = load_image(pic2_path) if os.path.exists(pic2_path) else None
            pic3 = load_image(pic3_path) if os.path.exists(pic3_path) else None
        except Exception:
            pic2 = None
            pic3 = None

        for idx, (t, v, m) in enumerate(self.action_opts):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (btn_w + spacing)
            y = start_y + row * (btn_h + spacing)
            w = btn_w
            h = btn_h
            # if this is the last item and the total count is odd, make it span both columns
            if (idx == len(self.action_opts) - 1) and (len(self.action_opts) % 2 == 1):
                x = start_x
                w = grid_w
            rect = (x, y, w, h)
            # pick background image: last long option gets pic3, others get pic2
            bg = pic3 if idx == len(self.action_opts) - 1 else pic2
            self.buttons.append(AnimatedButton(rect, t, self.font, color=(100,50,140), hover=(240,200,60), bg_image=bg))

        # Event/triggers
        self.event_queue = ["complaint1", "inspection1", "inspection2", "complaint2", "warning"]
        random.shuffle(self.event_queue)
        self.ticks = 0
        self.event_timer = 0
        self.current_event = None
        # event timing: use a random delay between events to reduce frequency
        # values in milliseconds
        self.event_delay_min = 5000  # 5 seconds
        self.event_delay_max = 9000  # 9 seconds
        self.next_event_delay = random.randint(self.event_delay_min, self.event_delay_max)
        # prepare two interactive buttons for event choices (stacked vertically when shown)
        # placeholders; rects will be positioned during render
        self.event_buttons = [AnimatedButton((0,0,300,64), 'Choice A', self.font, color=(100,60,60), hover=(160,100,100)),
                              AnimatedButton((0,0,300,64), 'Choice B', self.font, color=(60,100,60), hover=(100,160,100))]
        # map events to (main_text, choiceA_text, choiceB_text)
        self.event_texts = {
            'complaint1': ("A student is complaining loudly.", 'Brush off', 'Apologize & compensate'),
            'inspection1': ("A health inspector appears.", 'Bribe', 'Accept inspection'),
            'inspection2': ("Another inspector finds issues.", 'Fire temp', 'Take responsibility'),
            'complaint2': ("Another complaint arrives.", 'Dodge', 'Apologize'),
            'warning': ("The school sent a warning.", 'Ignore & continue', 'Fix sanitation'),
        }
        # try to load a custom event panel image (PNG) if the user provided one
        panel_path = os.path.join('assets', 'ui', 'PICTURE_event_panel.png')
        if os.path.exists(panel_path):
            try:
                # load the original image size so we can scale it preserving aspect ratio
                self.event_panel_img = load_image(panel_path)
                try:
                    self.event_panel_size = self.event_panel_img.get_size()
                except Exception:
                    self.event_panel_size = (800, 200)
            except Exception:
                self.event_panel_img = None
                self.event_panel_size = None
        else:
            self.event_panel_img = None
            self.event_panel_size = None
        # try to load textured button images for choices A/B
        try:
            bpa = os.path.join('assets', 'ui', 'button_cA.png')
            bpb = os.path.join('assets', 'ui', 'button_cB.png')
            self.event_button_imgs = [load_image(bpa) if os.path.exists(bpa) else None,
                                      load_image(bpb) if os.path.exists(bpb) else None]
        except Exception:
            self.event_button_imgs = [None, None]
        # instruction modal before first interaction in this scene
        self.show_instruction = True
        self.instruction_text = (
            "Business phase: pick an action to manage your canteen.\n"
            "Actions affect Integrity (hearts) and Money. Click to continue."
        )
        # typewriter effect state for instruction modal
        self.instruction_progress = 0.0
        self.instruction_speed = 120.0  # chars per second
        # track how many actions the player has taken; first event appears after 3 actions
        self.actions_done = 0
        self.first_event_triggered = False
        # effect multiplier: scale heart/money deltas to make each choice carry more weight
        # set to 5 so a single click applies ~5x effect as requested
        self.effect_multiplier = 5.0
        # prefer background image for business scene from assets/ui/background.png
        try:
            bg_path = os.path.join('assets', 'ui', 'background.png')
            self.bg = load_image(bg_path, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception:
            self.bg = None

    # helper to apply scaled heart change and return the actual applied value
    def apply_heart(self, delta):
        if delta == 0:
            return 0
        adj = int(round(delta * self.effect_multiplier))
        # ensure non-zero change for any non-zero input
        if adj == 0:
            adj = 1 if delta > 0 else -1
        self.game.change_hearts(adj)
        return adj

    # helper to apply scaled money change and return the actual applied value
    def apply_money(self, delta):
        if delta == 0:
            return 0
        adj = int(round(delta * self.effect_multiplier))
        if adj == 0:
            adj = 1 if delta > 0 else -1
        self.game.change_money(adj)
        return adj

    def handle_events(self, events):
        for e in events:
            # if instruction modal visible, consume click to dismiss only
            if self.show_instruction:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if int(self.instruction_progress) < len(self.instruction_text):
                        self.instruction_progress = float(len(self.instruction_text))
                    else:
                        try:
                            if getattr(self.game, 'sound', None):
                                self.game.sound.play_click()
                        except Exception:
                            pass
                        self.show_instruction = False
                continue

            # If an event panel is active, block interaction with the underlying action buttons
            # and only allow the stacked event choice buttons to receive clicks.
            if self.current_event:
                for idx, btn in enumerate(self.event_buttons):
                    if btn.handle_event(e):
                        try:
                            if getattr(self.game, 'sound', None):
                                self.game.sound.play_click()
                        except Exception:
                            pass
                        choice = 'A' if idx == 0 else 'B'
                        self.resolve_event(self.current_event, choice)
                        break
                # consume the event regardless so underlying buttons do not react
                continue

            # No modal/event active: allow normal action button interaction
            for i, btn in enumerate(self.buttons):
                if btn.handle_event(e):
                    try:
                        if getattr(self.game, 'sound', None):
                            self.game.sound.play_click()
                    except Exception:
                        pass
                    heart_delta = self.action_opts[i][1]
                    money_delta = self.action_opts[i][2]
                    if heart_delta != 0:
                        applied_h = self.apply_heart(heart_delta)
                        applied_m = self.apply_money(money_delta) if money_delta else 0
                        self.game.add_log(f"Action: {self.action_opts[i][0]} (hearts {applied_h:+d}, money {applied_m:+d})")
                    else:
                        # still affect money for minor mistakes
                        applied_m = self.apply_money(money_delta)
                        self.game.add_log(f"Minor mistake chosen: {self.action_opts[i][0]} (money {applied_m:+d})")
                    # count action and trigger first event when threshold reached
                    self.actions_done += 1
                    # if hearts are in grey (4-7), count this choice toward apathy persistence
                    try:
                        if 4 <= self.game.hearts <= 7:
                            self.game.history['grey_choice_count'] = self.game.history.get('grey_choice_count', 0) + 1
                    except Exception:
                        pass

                    # check apathy immediate-trigger: require at least 5 choices made while in grey AND money >= 1500
                    try:
                        if (self.game.money >= 1500) and (self.game.history.get('grey_choice_count', 0) >= 5) and (4 <= self.game.hearts <= 7):
                            self.game.add_log('Apathy conditions met — triggering ending')
                            self.game.change_scene('ending')
                            return
                    except Exception:
                        pass

                    # trigger the first event after 2 actions to shorten playtime
                    if not self.first_event_triggered and self.actions_done >= 2 and self.event_queue:
                        self.current_event = self.event_queue.pop(0)
                        self.first_event_triggered = True

    def resolve_event(self, ev, choice):
        # Apply heart changes according to design
        if ev == 'complaint1':
            if choice == 'A':
                ah = self.apply_heart(-2)
                self.game.add_log(f'You dodge the complaint. (hearts {ah:+d})')
                # if already in black after this choice, increment consecutive negative counter
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                ah = self.apply_heart(+2)
                am = self.apply_money(-50)
                self.game.add_log(f'You apologize and compensate. (hearts {ah:+d}, money {am:+d})')
                # positive event choice: mark history
                try:
                    if ah and ah > 0:
                        self.game.history['chose_positive_event'] = True
                except Exception:
                    pass
        elif ev == 'inspection1':
            if choice == 'A':
                ah = self.apply_heart(-3)
                am = self.apply_money(-200)
                self.game.add_log(f'You bribe the inspector. (hearts {ah:+d}, money {am:+d})')
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                ah = self.apply_heart(0)
                am = self.apply_money(-50)
                self.game.add_log(f'You accept the inspection (整改 notice). (money {am:+d})')
                try:
                    # treat accepting inspection as a non-negative / positive choice for spiral logic
                    self.game.history['chose_positive_event'] = True
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = 0
                except Exception:
                    pass
        elif ev == 'inspection2':
            if choice == 'A':
                ah = self.apply_heart(-2)
                self.game.add_log(f'You fire a temp as a scapegoat. (hearts {ah:+d})')
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                ah = self.apply_heart(+1)
                self.game.add_log(f'You accept responsibility. (hearts {ah:+d})')
                try:
                    if ah and ah > 0:
                        self.game.history['chose_positive_event'] = True
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = 0
                except Exception:
                    pass
        elif ev == 'complaint2':
            if choice == 'A':
                ah = self.apply_heart(-1)
                self.game.add_log(f'You dodge the second complaint. (hearts {ah:+d})')
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                ah = self.apply_heart(+1)
                am = self.apply_money(-30)
                self.game.add_log(f'You genuinely apologize again. (hearts {ah:+d}, money {am:+d})')
                try:
                    if ah and ah > 0:
                        self.game.history['chose_positive_event'] = True
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = 0
                except Exception:
                    pass
        elif ev == 'warning':
            # final key divergence
            if choice == 'A':
                # ignore / continue operating
                # preserve the 'force to 0' semantic by applying a large negative value scaled
                ah = self.apply_heart(-999)
                self.game.add_log('You ignored the warning and kept operating.')
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                # accept sanitation improvements
                # stabilize in grey (no change)
                self.game.add_log('You chose to improve sanitation.')
                try:
                    # this is a positive choice logically
                    self.game.history['chose_positive_event'] = True
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = 0
                except Exception:
                    pass

        # generic post-event bookkeeping: count choices made while in grey and check apathy trigger
        try:
            if 4 <= self.game.hearts <= 7:
                self.game.history['grey_choice_count'] = self.game.history.get('grey_choice_count', 0) + 1
        except Exception:
            pass

        try:
            if (self.game.money >= 1500) and (self.game.history.get('grey_choice_count', 0) >= 5) and (4 <= self.game.hearts <= 7):
                self.game.add_log('Apathy conditions met — triggering ending')
                self.current_event = None
                self.game.change_scene('ending')
                return
        except Exception:
            pass

        # clear current event
        self.current_event = None

    def update(self, dt):
        # periodically trigger events until queue empty
        # advance typewriter for instruction modal
        if getattr(self, 'show_instruction', False) and int(self.instruction_progress) < len(self.instruction_text):
            self.instruction_progress += (dt * self.instruction_speed) / 1000.0
            if self.instruction_progress > len(self.instruction_text):
                self.instruction_progress = float(len(self.instruction_text))

        self.event_timer += dt
        # subsequent events (after the first) are triggered by timer
        if not self.current_event and self.event_queue and self.first_event_triggered and self.event_timer > self.next_event_delay:
            self.current_event = self.event_queue.pop(0)
            self.event_timer = 0
            # pick next random delay for subsequent event
            self.next_event_delay = random.randint(self.event_delay_min, self.event_delay_max)

        # Immediate forced ending: if player has all red hearts AND money < -500, end immediately
        try:
            if self.game.hearts >= 8 and self.game.money < -500:
                print(f"[BusinessScene.update] Immediate ending trigger: hearts={self.game.hearts}, money={self.game.money}")
                self.game.change_scene('ending')
                return
        except Exception:
            pass

        # check end of day condition: once all events processed -> show ending
        if not self.event_queue and not self.current_event:
            # If the player has high Integrity (all red hearts) but hasn't gone deep into debt,
            # don't end the run automatically — continue playing instead.
            # Specifically: when hearts >= 8 and money >= -500, skip the automatic ending.
            try:
                if self.game.hearts >= 8 and self.game.money >= -500:
                    print(f"[BusinessScene.update] Skipping ending (hearts={self.game.hearts}, money={self.game.money}) - continuing game")
                    return
            except Exception:
                pass
            # otherwise proceed to ending
            self.game.change_scene('ending')

    def render(self, surf):
        # draw scene background (prefer provided background.png)
        try:
            if getattr(self, 'bg', None):
                surf.blit(self.bg, (0, 0))
            else:
                surf.fill((45, 38, 28))
        except Exception:
            surf.fill((45, 38, 28))
        # draw scene title (so it will be dimmed by overlay when panel appears)
        title_y = 140
        title_text = "Business Hours - Manage your canteen"
        title_pos = (WINDOW_WIDTH//2, title_y)
        pink = (253, 105, 253)
        # draw pink outline as a simple stroke
        outline_s = self.title_font.render(title_text, True, pink)
        for ox, oy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            surf.blit(outline_s, outline_s.get_rect(center=(title_pos[0] + ox, title_pos[1] + oy)))
        title_s = self.title_font.render(title_text, True, (185,12,12))
        surf.blit(title_s, title_s.get_rect(center=title_pos))

        for b in self.buttons:
            b.draw(surf)

        # event box
        if self.current_event:
            # draw a dark overlay first so the event panel will be on top
            try:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                surf.blit(overlay, (0, 0))
            except Exception:
                pass

            ex, ey, ew, eh = (240, 260, 800, 200)
            # if the user provided a custom panel image, draw it scaled preserving aspect ratio
            if getattr(self, 'event_panel_img', None) and getattr(self, 'event_panel_size', None):
                try:
                    orig_w, orig_h = self.event_panel_size
                    # maximum allowed panel size to fit screen comfortably; allow upscaling
                    max_w = int(WINDOW_WIDTH * 0.9)
                    max_h = int(WINDOW_HEIGHT * 0.9)
                    scale = min(max_w / orig_w, max_h / orig_h)
                    sw = max(1, int(orig_w * scale))
                    sh = max(1, int(orig_h * scale))
                    panel_surf = pygame.transform.smoothscale(self.event_panel_img, (sw, sh))
                    # center horizontally
                    px = (WINDOW_WIDTH - sw) // 2
                    # existing small vertical offset retained, then move the whole UI up by an additional 200px
                    # move the whole panel up by an additional 400px (200px earlier + 200px requested)
                    extra_up = 400
                    py = max(20, (WINDOW_HEIGHT - sh) // 2 - 40 - 80 - extra_up)
                    surf.blit(panel_surf, (px, py))
                    # override ex/ey/ew/eh to the scaled panel for layout of text/buttons
                    ex, ey, ew, eh = px, py, sw, sh
                except Exception:
                    pygame.draw.rect(surf, (20,20,20), (ex,ey,ew,eh), border_radius=10)
                    pygame.draw.rect(surf, (80,80,80), (ex+8,ey+8,ew-16,eh-16), border_radius=8)
            else:
                # if no panel image, just draw the plain box but moved up by 200px as well
                try:
                    extra_up = 400
                    ey = max(20, ey - extra_up)
                except Exception:
                    pass
                pygame.draw.rect(surf, (20,20,20), (ex,ey,ew,eh), border_radius=10)
                pygame.draw.rect(surf, (80,80,80), (ex+8,ey+8,ew-16,eh-16), border_radius=8)
            ef = load_font("assets/fonts/m6x11.ttf", 32)
            # split main event description and two choice labels
            main_text, a_text, b_text = self.event_texts.get(self.current_event, ('', 'Choice A', 'Choice B'))
            # compute stacked button sizes and positions (centered horizontally inside event box)
            # use relative paddings based on panel size so buttons/text stay inside image
            left_pad = int(ew * 0.12)
            top_pad = int(eh * 0.12)
            choice_w = ew - left_pad * 2
            choice_h = max(48, int(eh * 0.17))
            cx = ex + (ew - choice_w) // 2
            # place buttons in the lower portion of the panel to leave space for wrapped text above
            # move only the options block up by 200px (user requested). Keep main text position unchanged.
            top_y = ey + int(eh * 0.58) - 200
            # clamp so buttons don't go above the panel top
            top_y = max(ey + 8, top_y)
            gap = 16
            bottom_y = top_y + choice_h + gap

            # update button rects and texts before drawing so they respond correctly
            self.event_buttons[0].rect = pygame.Rect(cx, top_y, choice_w, choice_h)
            self.event_buttons[0].text = a_text
            self.event_buttons[1].rect = pygame.Rect(cx, bottom_y, choice_w, choice_h)
            self.event_buttons[1].text = b_text

            # draw wrapped main text inside the upper area of the panel
            content_x = ex + left_pad
            content_w = ew - left_pad * 2
            text_font = ef
            wrapped = wrap_text(main_text, text_font, content_w)
            line_h = text_font.get_linesize()
            # compute starting y so the block is above the buttons with a small margin
            text_block_h = len(wrapped) * line_h
            # move main event text up by 300px relative to its computed position
            text_start_y = max(ey + top_pad, top_y - 16 - text_block_h)
            # previously text was pulled up by 120px; move it down 100px relative to that
            # (i.e. apply only a 20px upward shift from computed position)
            text_start_y = max(10, text_start_y - 20)
            for i, ln in enumerate(wrapped):
                txt_surf = text_font.render(ln, True, (185,12,12))
                surf.blit(txt_surf, (content_x, text_start_y + i * line_h))

            # draw buttons stacked vertically; prefer textured button images if provided
            for idx, btn in enumerate(self.event_buttons):
                bimg = None
                try:
                    bimg = self.event_button_imgs[idx]
                except Exception:
                    bimg = None
                if bimg:
                    try:
                        bi = pygame.transform.smoothscale(bimg, (btn.rect.width, btn.rect.height))
                        surf.blit(bi, btn.rect.topleft)
                        # draw the label centered on the image
                        lab = btn.font.render(btn.text, True, (255,255,255))
                        surf.blit(lab, lab.get_rect(center=btn.rect.center))
                    except Exception:
                        btn.draw(surf)
                else:
                    btn.draw(surf)

        # draw instruction modal if visible (over everything)
        if getattr(self, 'show_instruction', False):
            # dim the underlying scene so the modal becomes the primary focus
            try:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                surf.blit(overlay, (0, 0))
            except Exception:
                pass

            box_w, box_h = 760, 160
            bx = (WINDOW_WIDTH - box_w)//2
            by = (WINDOW_HEIGHT - box_h)//2
            panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            # instruction modal color: #64d591 with 80% opacity (alpha=204)
            panel.fill((100, 213, 145, 204))
            # pink outline #fd69fd for the panel border
            pygame.draw.rect(panel, (253,105,253), (0,0,box_w,box_h), width=2, border_radius=8)
            f = load_font("assets/fonts/m6x11.ttf", 24)
            # show partially-typed text according to instruction_progress
            visible = getattr(self, 'instruction_text', '')[:int(getattr(self, 'instruction_progress', 0))]
            lines = visible.split('\n')
            for i, ln in enumerate(lines):
                panel.blit(f.render(ln, True, (240,240,240)), (18, 18 + i*28))
            hint = f.render('Click to continue', True, (200,200,200))
            panel.blit(hint, (box_w - hint.get_width() - 12, box_h - hint.get_height() - 12))
            surf.blit(panel, (bx, by))


class EndingScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 28)
        # larger title for ending
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 56)
        # load background image, prefer png then jpg/jpeg
        bg_path = None
        for ext in ('.png', '.jpg', '.jpeg'):
            p = os.path.join('assets', 'ui', f'PICTURE_background{ext}')
            if os.path.exists(p):
                bg_path = p
                break
        if not bg_path:
            bg_path = os.path.join('assets', 'ui', 'PICTURE_background.png')
        self.bg = load_image(bg_path, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # SceneBase was moved earlier in the file; no inner class needed here.
    def start(self):
        # determine ending text based on game.hearts and history
        v = self.game.hearts
        g = self.game.history
        m = self.game.money
        # debug log to help diagnose ending selection issues
        try:
            print(f"[EndingScene.start] hearts={v}, money={m}, history={g}")
        except Exception:
            pass
        # Apathy (strict): hearts currently in grey and player made >=5 choices while in grey AND money >= 1500
        try:
            if (m is not None) and (m >= 1500) and (4 <= v <= 7) and (g.get('grey_choice_count', 0) >= 5):
                self.key = 'apathy'
            else:
                self.key = None
        except Exception:
            self.key = None
        if self.key != 'apathy':
            if v <= 3:
                # When in black-heart range, check Spiral (strict, all required) first.
                try:
                    spiral_ok = (
                        g.get('had_grey') and
                        g.get('chose_positive_event') and
                        g.get('ended_black') and
                        (g.get('post_black_negative_consec', 0) >= 4) and
                        (g.get('last_negative_choice_money', 0) > 900)
                    )
                except Exception:
                    spiral_ok = False

                if spiral_ok:
                    self.key = 'spiral'
                else:
                    # 1A triggers if ANY of these hold:
                    # 1) grey-to-black happened quickly (few steps)
                    # 2) never chose a positive event option
                    # 3) after dropping to black, hearts never rose and only decreased
                    cond_quick_grey_to_black = False
                    cond_no_positive = False
                    cond_only_decrease_after_black = False
                    try:
                        if g.get('had_grey') and g.get('black_step') and g.get('grey_step'):
                            if (g.get('black_step') - g.get('grey_step')) <= 3:
                                cond_quick_grey_to_black = True
                    except Exception:
                        cond_quick_grey_to_black = False
                    try:
                        if not g.get('chose_positive_event'):
                            cond_no_positive = True
                    except Exception:
                        cond_no_positive = False
                    try:
                        if g.get('ended_black') and not g.get('post_black_increased') and g.get('post_black_decrease_count', 0) > 0:
                            cond_only_decrease_after_black = True
                    except Exception:
                        cond_only_decrease_after_black = False

                    if cond_quick_grey_to_black or cond_no_positive or cond_only_decrease_after_black:
                        self.key = '1A'
                    else:
                        # fallback for other black-heart cases
                        self.key = '1A'
            elif v >= 8:
                # red-heart branch unchanged: keep best_red/1B logic
                if m < -500:
                    self.key = 'best_red'
                else:
                    self.key = '1B'
            else:
                # default mid-range -> apathy fallback (if not already matched earlier)
                self.key = 'apathy'

        # try to load a provided ending image for this key (prefer artist PNGs)
        try:
            # explicit mapping from ending key -> filename (overrides the simple pattern)
            ending_filename_map = {
                'spiral': 'ending_spiral.png',
                '1A': 'ending_1A.png',
                'best_red': 'ending_1B.png',
                'apathy': 'ending_apathy.png',
            }
            fname = ending_filename_map.get(self.key, f'ending_{self.key}.png')
            ending_png = os.path.join('assets', 'ui', fname)
            if os.path.exists(ending_png):
                # cache a full-window scaled version so we don't rescale every frame
                try:
                    self._ending_img = load_image(ending_png, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    self._ending_img_path = ending_png
                    print(f"[EndingScene.start] Using ending image: {ending_png}")
                except Exception:
                    self._ending_img = None
            else:
                self._ending_img = None
        except Exception:
            self._ending_img = None
        # prepare title/body/subtitle strings and typewriter state
        try:
            # default single-line bodies for simple endings
            if self.key == 'spiral':
                self.title_text = 'Late Repentance and the Final Fall'
                self.title_color = (160,60,60)
                self.body_full = (
                    'The harsh reality and the lure of profit proved too strong.\n'
                    'You tasted purity, yet chose to forget it, sinking into a despair deeper than when you began.\n'
                    'However, the ledger on your desk shows you earned more money than ever before.\n'
                    'You won the money, but lost yourself.\n'
                )
                # remove hearts/money summary line per user request
                self.sub_text = ''
            elif self.key == '1A':
                self.title_text = 'Termination of Business'
                self.title_color = (220,50,50)
                self.body_full = (
                    'Your canteen has been replaced; a competitor has taken your spot.\n'
                    'The apathy and corruption you poured into the food eventually returned to you.\n'
                    'Following multiple complaints and inspections, the school board decisively removed you from this lucrative spot.\n'
                    'You lost, because your evil heart was too obvious.\n'
                )
                # remove hearts summary line
                self.sub_text = ''
            elif self.key == 'apathy':
                self.title_text = 'The Art of Moderate Survival'
                # title color changed to #b90c0c
                self.title_color = (185,12,12)
                self.body_full = (
                    'Congratulations! You achieved Apathy status, triggering the Moderate Ending: Continued Operation.\n'
                    'You learned to strike the "just right" balance between conscience and profit: no major issues, but not too much conscience either.\n'
                    'You avoided all noticeable extreme actions, quietly making money in the grey area.\n'
                )
                # remove hearts/money summary line
                self.sub_text = ''
            elif self.key == 'best_red':
                self.title_text = 'The Collapse of Idealism'
                self.title_color = (80,180,120)
                # updated per-user text: each sentence ends with a newline for centered, typewriter rendering
                self.body_full = (
                    'Your dishes were clean, delicious, and generous: a rare find.\n'
                    "But an overly idealistic business model prevents you from making a profit.\n"
                    'You ultimately lose to business reality.\n'
                    'Your conscience never failed, but your canteen did.\n'
                )
                # remove hearts/money summary line
                self.sub_text = ''
            else:
                # generic fallback
                self.title_text = 'Late Repentance and the Final Fall'
                self.title_color = (160,60,60)
                self.body_full = 'You once had a chance to turn back, but were ultimately consumed by the darkness.'
                # remove hearts summary line
                self.sub_text = ''
        except Exception:
            self.title_text = 'Ending'
            self.title_color = (200,200,200)
            self.body_full = ''
            self.sub_text = ''

        # typewriter state for the narrative body
        self.body_progress = 0.0
        self.body_speed = 120.0  # chars per second

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # if body is still typing, complete instantly; otherwise return to title
                try:
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                if getattr(self, 'body_progress', 0) < len(getattr(self, 'body_full', '')):
                    self.body_progress = float(len(getattr(self, 'body_full', '')))
                else:
                    self.game.change_scene('title')

    def update(self, dt):
        # advance typewriter for body text
        if getattr(self, 'body_progress', 0.0) < len(getattr(self, 'body_full', '')):
            self.body_progress += (dt * getattr(self, 'body_speed', 120.0)) / 1000.0
            if self.body_progress > len(self.body_full):
                self.body_progress = float(len(self.body_full))

    def render(self, surf):
        # draw provided ending image if available, otherwise fall back to generic background
        try:
            img = getattr(self, '_ending_img', None)
            if img:
                surf.blit(img, (0, 0))
            else:
                surf.blit(self.bg, (0, 0))
        except Exception:
            surf.blit(self.bg, (0,0))
        v = self.game.hearts
        # render title (moved down by 170px earlier, now shift up by 100px per request)
        title_text = getattr(self, 'title_text', 'Ending')
        title_color = tuple(getattr(self, 'title_color', (200,200,200)))
        # debug: print chosen ending key
        try:
            print(f"[EndingScene.start] chosen ending key: {getattr(self, 'key', None)}")
        except Exception:
            pass

        # center title: original base y was 120; moved down by 170 then shift up overall by 100
        title_y = 120 + 170 - 100
        key = getattr(self, 'key', None)
        # draw special outlines requested by the user:
        # - 1A: white outline
        # - apathy: pink outline (#fd69fd) and title color already set to #b90c0c in start()
        outline_col = None
        if key == '1A':
            outline_col = (255,255,255)
        elif key == 'apathy':
            outline_col = (253,105,253)

        if outline_col is not None:
            outline_s = self.title_font.render(title_text, True, outline_col)
            for ox, oy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
                surf.blit(outline_s, outline_s.get_rect(center=(WINDOW_WIDTH//2 + ox, title_y + oy)))

        title_s = self.title_font.render(title_text, True, title_color)
        surf.blit(title_s, title_s.get_rect(center=(WINDOW_WIDTH//2, title_y)))

        # render narrative body with typewriter effect. center the visible block around y=400 then shift up 100px
        visible = getattr(self, 'body_full', '')[:int(getattr(self, 'body_progress', 0))]
        lines = visible.split('\n') if isinstance(visible, str) else [str(visible)]
        # remove any empty trailing lines
        lines = [ln for ln in lines if ln]
        line_h = self.font.get_linesize()
        block_h = line_h * max(1, len(lines))
        start_y = 400 - block_h // 2 - 100
        # body text color: for 'apathy' ending use #b90c0c (185,12,12), otherwise default light gray
        body_color = (185, 12, 12) if getattr(self, 'key', None) == 'apathy' else (230, 230, 230)
        for i, ln in enumerate(lines):
            txt_surf = self.font.render(ln, True, body_color)
            surf.blit(txt_surf, txt_surf.get_rect(center=(WINDOW_WIDTH//2, start_y + i * line_h + line_h//2)))

        # subtitle (single line) below the body
        sub_color = (185, 12, 12) if getattr(self, 'key', None) == 'apathy' else (255, 255, 255)
        sub_surf = self.font.render(getattr(self, 'sub_text', ''), True, sub_color)
        surf.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH//2, start_y + block_h + 40)))
        # move hint to bottom-right; hint color matches body for apathy to keep consistent
        hint_color = (185, 12, 12) if getattr(self, 'key', None) == 'apathy' else (200, 200, 200)
        hint = self.font.render('Click anywhere to return to title and start a new day.', True, hint_color)
        surf.blit(hint, (WINDOW_WIDTH - 20 - hint.get_width(), WINDOW_HEIGHT - 20 - hint.get_height()))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Evil Canteen Simulator')
        self.clock = pygame.time.Clock()
        # sound manager: loads optional SFX/BGM from assets/sounds/
        try:
            self.sound = SoundManager()
            # start background music if available
            try:
                self.sound.play_bgm(loop=True)
            except Exception:
                pass
        except Exception:
            self.sound = None
        # try to load custom heart images from assets/ui/ if present
        heart_images = {
            'red': None,
            'grey': None,
            'black': None,
            'empty': None,
        }
        try:
            heart_images['red'] = load_image('assets/ui/heart_red.png')
        except Exception:
            pass
        try:
            heart_images['grey'] = load_image('assets/ui/heart_grey.png')
        except Exception:
            pass
        try:
            heart_images['black'] = load_image('assets/ui/heart_black.png')
        except Exception:
            pass
        try:
            heart_images['empty'] = load_image('assets/ui/heart_empty.png')
        except Exception:
            pass

        # try to load money icon
        try:
            self.money_icon = load_image('assets/ui/money.png')
        except Exception:
            self.money_icon = None

        self.heart_bar = HeartBar(10, images=heart_images)
        # HUD visibility flag: hide top-left/right values until Start is clicked
        self.show_hud = False
        # core state
        self.hearts = 10
        self.money = 0  # financial counter (profit positive, loss negative)
        self.history = {'had_grey': False, 'had_red_again': False, 'ended_black': False, 'chose_positive_event': False}
        # count how many player choices happened while hearts were in grey (4-7)
        self.history['grey_choice_count'] = 0
        # additional history / tracing for complex ending logic
        # steps track approximate action/event sequence indices
        self.step = 0
        # record when grey/black first happened (step number)
        self.history['grey_step'] = None
        self.history['black_step'] = None
        # after black tracking
        self.history['post_black_decrease_count'] = 0
        self.history['post_black_increased'] = False
        # consecutive negative event choices after black
        self.history['post_black_negative_consec'] = 0
        # record last money value when a negative event choice occurred after black
        self.history['last_negative_choice_money'] = 0
        self.logs = []

        # scenes
        self.scenes = {
            'title': TitleScene(self),
            'prep': PrepScene(self),
            'business': BusinessScene(self),
            'ending': EndingScene(self),
        }
        self.current = self.scenes['title']

    def start_new_run(self):
        # reset state
        self.hearts = 10
        self.money = 0
        self.history = {'had_grey': False, 'had_red_again': False, 'ended_black': False, 'chose_positive_event': False, 'grey_choice_count': 0}
        self.logs = []
        # recreate business scene for fresh event queue
        self.scenes['business'] = BusinessScene(self)
        self.scenes['ending'] = EndingScene(self)
        # show HUD from now on
        self.show_hud = True
        self.change_scene('prep')

    def change_money(self, delta):
        self.money += delta
        # record a special history flag if money went negative at any moment
        if self.money < 0:
            self.history['had_negative_money'] = True

    def change_scene(self, key):
        self.current = self.scenes[key]
        if hasattr(self.current, 'start'):
            try:
                self.current.start()
            except Exception:
                pass

    def change_hearts(self, delta):
        # increment step so we can reason about sequence/timing
        try:
            self.step += 1
        except Exception:
            self.step = getattr(self, 'step', 0) + 1

        prev = getattr(self, 'hearts', 10)
        if delta == -999:
            self.hearts = 0
        else:
            self.hearts = max(0, min(10, self.hearts + delta))

        # update history: detect entry into grey range
        try:
            if not self.history.get('had_grey') and 4 <= self.hearts <= 7:
                self.history['had_grey'] = True
                self.history['grey_step'] = self.step
        except Exception:
            pass

        # detect re-red (if rose after grey)
        try:
            if self.hearts >= 8 and self.history.get('had_grey'):
                self.history['had_red_again'] = True
        except Exception:
            pass

        # detect entry into black range
        try:
            if not self.history.get('ended_black') and self.hearts <= 3:
                self.history['ended_black'] = True
                self.history['black_step'] = self.step
        except Exception:
            pass

        # track changes that happen after black has occurred
        try:
            if self.history.get('ended_black'):
                if delta < 0:
                    self.history['post_black_decrease_count'] = self.history.get('post_black_decrease_count', 0) + 1
                elif delta > 0:
                    self.history['post_black_increased'] = True
        except Exception:
            pass

    def add_log(self, text):
        self.logs.append(text)

    def draw_logs(self, surf):
        # show last 5 logs in bottom-left
        if not self.logs:
            return
        font = load_font("assets/fonts/m6x11.ttf", 18)
        lines = self.logs[-5:]
        padding = 8
        line_h = 20
        box_w = 520
        box_h = padding*2 + line_h * len(lines)
        x = 20
        y = WINDOW_HEIGHT - box_h - 20
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        # pink background #fd69fd with 70% opacity
        box.fill((253, 105, 253, 178))
        for i, l in enumerate(lines):
            txt = font.render(l, True, (230, 230, 230))
            box.blit(txt, (padding, padding + i * line_h))
        surf.blit(box, (x, y))

    def draw_debug(self, surf):
        # small debug panel top-left: FPS, hearts, money, event queue status
        f = load_font("assets/fonts/m6x11.ttf", 16)
        fps = int(self.clock.get_fps())
        lines = [f"FPS: {fps}", f"Hearts: {self.hearts}", f"Money: {self.money:+d}"]
        # event queue info from business scene
        be = self.scenes.get('business')
        if be:
            try:
                qlen = len(be.event_queue)
                cur = be.current_event if be.current_event else 'none'
                lines.append(f"Events: {qlen} cur:{cur}")
            except Exception:
                lines.append('Events: ?')

        pad = 6
        w = 300
        h = pad*2 + 18 * len(lines)
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        # pink background #fd69fd with 70% opacity
        panel.fill((253, 105, 253, 178))
        for i, ln in enumerate(lines):
            panel.blit(f.render(ln, True, (220,220,220)), (pad, pad + i*18))
        surf.blit(panel, (10, 10))
    def draw_money(self, surf):
        # deprecated: draw_money replaced by draw_status (kept for compatibility)
        font = load_font("assets/fonts/m6x11.ttf", 18)
        txt = font.render(f"${self.money:+d}", True, (250, 220, 80))
        x = WINDOW_WIDTH - 20 - txt.get_width()
        y = 56
        surf.blit(txt, (x, y))

    def draw_status(self, surf):
        """Draw a compact status box at top-right containing hearts and money.
        Money is right-aligned with $ prefix and colored green (profit) or red (loss).
        """
        # make the status box wider and taller so hearts can be centered and prominent
        box_w = 360
        box_h = 110
        padding = 8
        x = WINDOW_WIDTH - box_w - 10
        y = 10
        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        # pink background #fd69fd with 70% opacity
        panel.fill((253, 105, 253, 178))

        # hearts: center the full row across the panel
        max_hearts = self.heart_bar.max
        # choose a size that fills the bar nicely
        heart_size = 28
        # compute spacing to spread hearts across width between padding
        avail_w = box_w - padding*2 - heart_size
        if max_hearts > 1:
            spacing = max(18, avail_w // (max_hearts - 1))
        else:
            spacing = 0
        total_row_w = heart_size + spacing * (max_hearts - 1)
        start_x = (box_w - total_row_w) // 2
        heart_y = 10
        self.heart_bar.draw(panel, self.hearts, x=start_x, y=heart_y, size=heart_size, spacing=spacing)

        # money text larger and right-aligned beneath hearts, with optional icon to its left
        font = load_font("assets/fonts/m6x11.ttf", 36)
        money_text = f"${self.money:+d}"
        color = (50, 200, 80) if self.money >= 0 else (220, 80, 80)
        txt = font.render(money_text, True, color)

        icon_w = icon_h = 0
        if getattr(self, 'money_icon', None):
            try:
                # scale icon slightly larger than text height for visibility
                icon_h = int(txt.get_height() * 1.1)  # 10% larger than text height
                icon_w = int(self.money_icon.get_width() * (icon_h / self.money_icon.get_height()))
                icon_s = pygame.transform.smoothscale(self.money_icon, (icon_w, icon_h))
            except Exception:
                icon_s = None
                icon_w = 0
                icon_h = 0
        else:
            icon_s = None

        # right-align the combined icon+text inside the panel
        total_w = icon_w + (6 if icon_w and txt.get_width() else 0) + txt.get_width()
        money_x = box_w - padding - total_w
        money_y = heart_y + heart_size + 8
        if icon_s:
            panel.blit(icon_s, (money_x, money_y))
            panel.blit(txt, (money_x + icon_w + 6, money_y))
        else:
            panel.blit(txt, (box_w - padding - txt.get_width(), money_y))

        # blit panel onto surface
        surf.blit(panel, (x, y))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    running = False
                # (removed quick-play E-key shortcut per user request)
            # delegate
            self.current.handle_events(events)
            try:
                self.current.update(dt)
            except Exception:
                pass
            # render
            self.current.render(self.screen)
            # draw HUD elements only after Start has been clicked
            if self.show_hud:
                # heart bar (standalone) and status/debug panels
                self.heart_bar.draw(self.screen, self.hearts)
                # draw debug panel
                self.draw_debug(self.screen)
                # draw status box (hearts + money) at top-right
                self.draw_status(self.screen)

            # draw logs (keep visible regardless of HUD state)
            self.draw_logs(self.screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()



