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
        self.btn_font = load_font("assets/fonts/m6x11.ttf", 32)
        # use the JPG background for the title screen explicitly
        self.bg = load_image(os.path.join('assets', 'ui', 'PICTURE_background.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
        # change Start/Quit button base color to #e5002b
        btn_color = (229, 0, 43)
        btn_hover = (255, 60, 80)
        self.start_btn = Button((WINDOW_WIDTH//2-180, 360, 360, 64), "Start Game", self.btn_font, color=btn_color, hover=btn_hover)
        self.quit_btn = Button((WINDOW_WIDTH//2-180, 440, 360, 64), "Quit", self.btn_font, color=btn_color, hover=btn_hover)

    def handle_events(self, events):
        for e in events:
            if self.start_btn.handle_event(e):
                self.game.start_new_run()
            if self.quit_btn.handle_event(e):
                pygame.quit(); sys.exit()

    def render(self, surf):
        surf.blit(self.bg, (0,0))
        # (figure removed per request)
        self.start_btn.draw(surf)
        self.quit_btn.draw(surf)


class PrepScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 26)
        w = 520
        # (text, heart_delta, money_delta)
        self.options = [
            ("Use expired ingredients (-2)", -2, +50),
            ("Ignore insect bodies (-1)", -1, +30),
            ("Ignore dirty utensils (-1)", -1, +20),
            ("Clean thoroughly (+0)", 0, -80),
        ]
        self.buttons = []
        left = 120
        top = 220
        for i, (t, v, m) in enumerate(self.options):
            rect = (left, top + i*80, w, 56)
            self.buttons.append(Button(rect, t, self.font, color=(100,50,140), hover=(240,200,60)))

        # instruction modal before any choice
        self.show_instruction = True
        self.instruction_text = (
            "Preparation phase: choose how you prepare the food.\n"
            "Each choice changes Integrity (hearts) and Money.\n"
            "Click anywhere to continue and make your selection."
        )

    def handle_events(self, events):
        # if instruction modal visible, consume clicks to dismiss only
        for e in events:
            if self.show_instruction:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.show_instruction = False
                continue

            for i, btn in enumerate(self.buttons):
                if btn.handle_event(e):
                    heart_delta = self.options[i][1]
                    money_delta = self.options[i][2]
                    self.game.change_hearts(heart_delta)
                    self.game.change_money(money_delta)
                    self.game.add_log(f"Prep choice: {self.options[i][0]} (money {money_delta:+d})")
                    # proceed to business after a choice
                    self.game.change_scene('business')

    def render(self, surf):
        surf.fill((30, 30, 30))
        title = self.font.render("Preparation - choose how to prepare for the day", True, (240,240,240))
        surf.blit(title, (80, 120))
        for b in self.buttons:
            b.draw(surf)

        # draw instruction modal on top if needed
        if getattr(self, 'show_instruction', False):
            box_w, box_h = 760, 160
            bx = (WINDOW_WIDTH - box_w)//2
            by = (WINDOW_HEIGHT - box_h)//2
            panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            panel.fill((12, 12, 12, 220))
            pygame.draw.rect(panel, (200,200,200), (0,0,box_w,box_h), width=2, border_radius=8)
            f = load_font("assets/fonts/m6x11.ttf", 20)
            lines = self.instruction_text.split('\n')
            for i, ln in enumerate(lines):
                panel.blit(f.render(ln, True, (240,240,240)), (18, 18 + i*28))
            hint = f.render('Click to continue', True, (200,200,200))
            panel.blit(hint, (box_w - hint.get_width() - 12, box_h - hint.get_height() - 12))
            surf.blit(panel, (bx, by))


class BusinessScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 22)
        # (text, heart_delta, money_delta)
        self.action_opts = [
            ("Do nothing about cockroaches (-1)", -1, +30),
            ("Use dirty plates (-1)", -1, +40),
            ("Give students very small portions (-1)", -1, +20),
            ("Serve wrong dish (0)", 0, -10),
        ]
        self.buttons = []
        left = 80
        top = 140
        w = 520
        for i, (t, v, m) in enumerate(self.action_opts):
            self.buttons.append(Button((left, top+i*70, w, 56), t, self.font, color=(100,50,140), hover=(240,200,60)))

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
        # instruction modal before each action phase or when events appear
        self.show_instruction = True
        self.instruction_text = (
            "Business phase: pick an action to manage your canteen.\n"
            "Actions affect Integrity (hearts) and Money. Click to continue."
        )

    def handle_events(self, events):
        for e in events:
            # if instruction modal visible, consume click to dismiss only
            if self.show_instruction:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.show_instruction = False
                continue

            for i, btn in enumerate(self.buttons):
                if btn.handle_event(e):
                    heart_delta = self.action_opts[i][1]
                    money_delta = self.action_opts[i][2]
                    if heart_delta != 0:
                        self.game.change_hearts(heart_delta)
                        self.game.change_money(money_delta)
                        self.game.add_log(f"Action: {self.action_opts[i][0]} (money {money_delta:+d})")
                    else:
                        # still affect money for minor mistakes
                        self.game.change_money(money_delta)
                        self.game.add_log(f"Minor mistake chosen: {self.action_opts[i][0]} (money {money_delta:+d})")
                    # do NOT re-show instruction modal after each action (only show once at scene start)

            if self.current_event and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # click responds to event choices (only when instruction dismissed)
                mx, my = e.pos
                # simple two-choice buttons in event box
                # left half = choice A, right half = choice B
                ex, ey, ew, eh = (240, 260, 800, 200)
                if ex <= mx <= ex+ew and ey <= my <= ey+eh:
                    # resolve event
                    choice = 'A' if mx < ex + ew//2 else 'B'
                    self.resolve_event(self.current_event, choice)

    def resolve_event(self, ev, choice):
        # Apply heart changes according to design
        if ev == 'complaint1':
            if choice == 'A':
                self.game.change_hearts(-2); self.game.add_log('You dodge the complaint.')
            else:
                self.game.change_hearts(+2); self.game.change_money(-50); self.game.add_log('You apologize and compensate. (money -50)')
        elif ev == 'inspection1':
            if choice == 'A':
                self.game.change_hearts(-3); self.game.change_money(-200); self.game.add_log('You bribe the inspector. (money -200)')
            else:
                self.game.change_hearts(0); self.game.change_money(-50); self.game.add_log('You accept the inspection (整改 notice). (money -50)')
        elif ev == 'inspection2':
            if choice == 'A':
                self.game.change_hearts(-2); self.game.add_log('You fire a temp as a scapegoat.')
            else:
                self.game.change_hearts(+1); self.game.add_log('You accept responsibility.')
        elif ev == 'complaint2':
            if choice == 'A':
                self.game.change_hearts(-1); self.game.add_log('You dodge the second complaint.')
            else:
                self.game.change_hearts(+1); self.game.change_money(-30); self.game.add_log('You genuinely apologize again. (money -30)')
        elif ev == 'warning':
            # final key divergence
            if choice == 'A':
                # ignore / continue operating
                self.game.change_hearts(-999)  # force to 0
                self.game.add_log('You ignored the warning and kept operating.')
            else:
                # accept sanitation improvements
                # stabilize in grey (no change)
                self.game.add_log('You chose to improve sanitation.')

        # clear current event
        self.current_event = None

    def update(self, dt):
        # periodically trigger events until queue empty
        self.event_timer += dt
        if not self.current_event and self.event_queue and self.event_timer > self.next_event_delay:
            self.current_event = self.event_queue.pop(0)
            self.event_timer = 0
            # pick next random delay for subsequent event
            self.next_event_delay = random.randint(self.event_delay_min, self.event_delay_max)
            # do not show instruction modal for each event; events are interactive immediately

        # check end of day condition: once all events processed -> show ending
        if not self.event_queue and not self.current_event:
            # go to ending
            self.game.change_scene('ending')

    def render(self, surf):
        surf.fill((45, 38, 28))
        title = self.font.render("Business Hours - Manage your canteen", True, (240,240,240))
        surf.blit(title, (80, 80))
        for b in self.buttons:
            b.draw(surf)

        # event box
        if self.current_event:
            ex, ey, ew, eh = (240, 260, 800, 200)
            pygame.draw.rect(surf, (20,20,20), (ex,ey,ew,eh), border_radius=10)
            pygame.draw.rect(surf, (80,80,80), (ex+8,ey+8,ew-16,eh-16), border_radius=8)
            ef = load_font("assets/fonts/m6x11.ttf", 24)
            text_map = {
                'complaint1': 'A student is complaining loudly. A: Brush off / B: Apologize & compensate',
                'inspection1': 'A health inspector appears. A: Bribe / B: Accept inspection',
                'inspection2': 'Another inspector finds issues. A: Fire temp / B: Take responsibility',
                'complaint2': 'Another complaint arrives. A: Dodge / B: Apologize',
                'warning': 'The school sent a warning. A: Ignore & continue / B: Fix sanitation',
            }
            lines = ef.render(text_map.get(self.current_event, ''), True, (255,255,255))
            surf.blit(lines, (ex+20, ey+20))
            # simple left/right choice visuals
            left_area = pygame.Rect(ex+40, ey+100, ew//2-80, 64)
            right_area = pygame.Rect(ex+ew//2+40, ey+100, ew//2-80, 64)
            pygame.draw.rect(surf, (100,60,60), left_area, border_radius=8)
            pygame.draw.rect(surf, (60,100,60), right_area, border_radius=8)
            la = load_font("assets/fonts/m6x11.ttf", 20)
            surf.blit(la.render('Choice A', True, (255,255,255)), left_area.center)
            surf.blit(la.render('Choice B', True, (255,255,255)), right_area.center)

        # draw instruction modal if visible (over everything)
        if getattr(self, 'show_instruction', False):
            box_w, box_h = 760, 160
            bx = (WINDOW_WIDTH - box_w)//2
            by = (WINDOW_HEIGHT - box_h)//2
            panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            panel.fill((10, 10, 10, 220))
            pygame.draw.rect(panel, (200,200,200), (0,0,box_w,box_h), width=2, border_radius=8)
            f = load_font("assets/fonts/m6x11.ttf", 20)
            lines = getattr(self, 'instruction_text', '').split('\n')
            for i, ln in enumerate(lines):
                panel.blit(f.render(ln, True, (240,240,240)), (18, 18 + i*28))
            hint = f.render('Click to continue', True, (200,200,200))
            panel.blit(hint, (box_w - hint.get_width() - 12, box_h - hint.get_height() - 12))
            surf.blit(panel, (bx, by))


class EndingScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 28)
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 48)
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
        # 1A: black hearts failure
        if v <= 3:
            # check for spiral: had grey then returned to red then ended black
            if g.get('had_grey') and g.get('had_red_again') and g.get('ended_black'):
                self.key = 'spiral'
            else:
                self.key = '1A'
        elif v >= 8:
            # 1B triggers when player kept red hearts (integrity) but ended in financial loss
            if m < 0:
                self.key = '1B'
            else:
                # stayed red and financially non-negative -> treat as best integrity ending
                self.key = 'best_red'
        else:
            self.key = 'apathy'

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # return to title
                self.game.change_scene('title')

    def render(self, surf):
        surf.blit(self.bg, (0,0))
        v = self.game.hearts
        if self.key == '1A':
            title = self.title_font.render('Termination of Business', True, (220,50,50))
            body = 'Your canteen has been replaced; a competitor has taken your spot.'
            sub = '0 Black Hearts'
        elif self.key == '1B':
            title = self.title_font.render('The Collapse of Idealism', True, (200,180,80))
            body = 'You received the highest praise, but also a notice of financial loss.'
            sub = f'{v} Red Hearts'
        elif self.key == 'apathy':
            title = self.title_font.render('The Art of Moderate Survival', True, (180,180,180))
            body = 'Congratulations! You achieved Apathy status, continued operation.'
            sub = f'{v} Grey Hearts'
        else:
            title = self.title_font.render('Late Repentance and the Final Fall', True, (160,60,60))
            body = 'You once had a chance to turn back, but were ultimately consumed by the darkness.'
            sub = f'{v} Black Hearts'

        if self.key == 'best_red':
            title = self.title_font.render('Integrity Preserved, But You Survived', True, (80,180,120))
            body = 'Your canteen stayed true to its values and did not collapse financially.'
            sub = f'{v} Red Hearts | Money {self.game.money:+d}'

        surf.blit(title, (80, 120))
        btxt = self.font.render(body, True, (230,230,230))
        surf.blit(btxt, (80, 200))
        surf.blit(self.font.render(sub, True, (255,255,255)), (80, 260))
        hint = self.font.render('Click anywhere to return to title and start a new day.', True, (200,200,200))
        surf.blit(hint, (80, 340))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Evil Canteen Simulator')
        self.clock = pygame.time.Clock()
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
        self.history = {'had_grey': False, 'had_red_again': False, 'ended_black': False}
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
        self.history = {'had_grey': False, 'had_red_again': False, 'ended_black': False}
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
        if delta == -999:
            self.hearts = 0
        else:
            self.hearts = max(0, min(10, self.hearts + delta))
        # update history
        if 4 <= self.hearts <= 7:
            self.history['had_grey'] = True
        if self.hearts >= 8 and self.history.get('had_grey'):
            self.history['had_red_again'] = True
        if self.hearts <= 3:
            self.history['ended_black'] = True

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
        box.fill((10, 10, 10, 180))
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
        panel.fill((10, 10, 10, 180))
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
        panel.fill((18, 14, 22, 220))

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



