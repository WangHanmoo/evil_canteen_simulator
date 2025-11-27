import os
import sys
import random
import math
import pygame

# Evil Canteen Simulator - Mr.TomatoS风格版本
# 整合了main.py的游戏流程和mr_canteen.py的Mr.TomatoS风格视觉效果

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FPS = 60

# ==================== Mr.TomatoS风格颜色定义 ====================
COLOR_BG_WARM = (255, 245, 220)      # 温馨背景 - 奶油色
COLOR_BG_CREEPY = (40, 20, 30)       # 诡异背景 - 暗红黑
COLOR_TEXT_NORMAL = (80, 60, 50)     # 普通文字 - 棕色
COLOR_TEXT_CREEPY = (180, 30, 30)    # 恐怖文字 - 血红
COLOR_ACCENT = (220, 80, 60)         # 强调色 - 番茄红
COLOR_PANEL = (255, 250, 240)        # 面板色 - 米白
COLOR_PANEL_DARK = (60, 30, 40)      # 暗色面板


def lerp(a, b, t):
    """线性插值"""
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """颜色线性插值"""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(min(len(c1), len(c2))))


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


# ==================== 存档管理系统 ====================
import json

SAVE_FILE = "save_data.json"

# 所有结局定义
ALL_ENDINGS = {
    '1A': {
        'name': 'Termination of Business',
        'description': 'Your canteen was shut down due to your obvious evil.',
        'color': (220, 50, 50)
    },
    '1B': {
        'name': 'Late Repentance',
        'description': 'You tried to change but it was too late.',
        'color': (180, 120, 60)
    },
    'spiral': {
        'name': 'Late Repentance and the Final Fall',
        'description': 'You won the money, but lost yourself.',
        'color': (160, 60, 60)
    },
    'apathy': {
        'name': 'The Art of Moderate Survival',
        'description': 'You mastered the balance between conscience and profit.',
        'color': (185, 12, 12)
    },
    'best_red': {
        'name': 'The Collapse of Idealism',
        'description': 'Your conscience never failed, but your canteen did.',
        'color': (80, 180, 120)
    }
}

def load_save_data():
    """加载存档数据"""
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {'unlocked_endings': []}

def save_data(data):
    """保存存档数据"""
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def unlock_ending(ending_key):
    """解锁一个结局"""
    data = load_save_data()
    if ending_key not in data['unlocked_endings']:
        data['unlocked_endings'].append(ending_key)
        save_data(data)

def get_unlocked_endings():
    """获取已解锁的结局列表"""
    data = load_save_data()
    return data.get('unlocked_endings', [])


# ==================== 食堂老板角色 (Mr.TomatoS风格) ====================

# 老板讽刺对话库
BOSS_DIALOGUES = {
    # 闲聊对话 - 点击老板时随机触发
    'idle': [
        "What? Work faster!",
        "Staring won't earn money!",
        "Every penny counts...",
        "Profit is all that matters.",
        "Students won't notice anyway.",
        "Quality? Never heard of it.",
        "Fresh? It's fresh enough!",
        "Health code? More like suggestions.",
        "I didn't see any cockroaches...",
        "That's not mold, it's seasoning!",
    ],
    # 负面选择后的开心对话
    'happy_negative': [
        "Smart choice! Save every cent!",
        "Now you're thinking like me!",
        "Who needs quality anyway?",
        "Excellent! Profit above all!",
        "That's my apprentice!",
        "Money doesn't grow on trees!",
        "Students have strong stomachs!",
        "Hygiene is overrated!",
        "Expired? More like 'vintage'!",
        "Perfect! More money for us!",
    ],
    # 正面选择后的生气对话
    'angry_positive': [
        "Waste of money!",
        "Are you trying to bankrupt me?!",
        "Quality doesn't pay bills!",
        "You call that good business?!",
        "My wallet is crying!",
        "Why spend money on THAT?!",
        "You'll regret this kindness!",
        "Being nice won't make you rich!",
        "Stop being so... ethical!",
        "Money out the window!",
    ],
    # 低诚信时的邪恶对话
    'creepy': [
        "Hehehe... Perfect...",
        "They suspect nothing...",
        "We're doing so well...",
        "Just a little more...",
        "No one can stop us now...",
        "The money keeps flowing...",
        "Ethics? What's that?",
        "We're unstoppable!",
        "Soon we'll be rich!",
        "Keep going... yes...",
    ],
    # 诚信恢复时的不满对话
    'upset_recovery': [
        "Why are you being nice?!",
        "Stop wasting money!",
        "This isn't charity!",
        "Ugh, too much conscience!",
        "You're ruining our profits!",
        "What happened to greed?",
        "Being good costs too much!",
        "I miss the old you...",
    ],
    # 事件相关的讽刺
    'complaint': [
        "Just ignore them!",
        "Complainers gonna complain!",
        "They'll forget by tomorrow.",
        "One less customer, who cares?",
    ],
    'inspector': [
        "Quick, hide everything!",
        "Just smile and bribe!",
        "Inspectors love 'gifts'!",
        "Play dumb, works every time!",
    ],
    'warning': [
        "Rules are meant to be bent!",
        "They're bluffing, trust me!",
        "We've survived worse!",
        "Just lay low for a while...",
    ],
}

class CanteenBoss:
    """
    食堂老板 - 类似Mr.TomatoS的角色
    眼睛跟随鼠标、会变大、瞳孔变红
    """
    def __init__(self, x, y, size=250):
        self.x = x
        self.y = y
        self.size = size
        
        # 状态
        self.mood = "neutral"  # neutral, happy, angry, creepy
        self.creepy_level = 0.0  # 诡异程度 0.0-1.0
        
        # 动画
        self.eye_offset = [0, 0]
        self.mouth_open = 0.0
        self.shake_amount = 0
        self.pulse = 0
        
        # 表情参数
        self.eye_size = 35
        self.pupil_size = 12
        self.blink_timer = 0
        self.is_blinking = False
        
        # 对话
        self.current_text = ""
        self.text_timer = 0
        
        # 互动
        self.click_cooldown = 0
        self.idle_timer = 0
        self.idle_chat_interval = 5000  # 5秒自动说话一次
        self.last_hearts = 10
        
        # 颜色会随诡异程度变化
        self.face_color = (255, 200, 150)
        self.eye_color = (255, 255, 255)
        self.pupil_color = (30, 30, 30)
        
        # 点击区域
        self.click_rect = pygame.Rect(x - 80, y - 100, 160, 250)
    
    def handle_click(self, pos):
        """处理点击事件"""
        if self.click_cooldown > 0:
            return False
        
        # 更新点击区域位置
        self.click_rect = pygame.Rect(self.x - 80, self.y - 100, 160, 250)
        
        if self.click_rect.collidepoint(pos):
            self.click_cooldown = 1000  # 1秒冷却
            self._say_random_dialogue()
            return True
        return False
    
    def _say_random_dialogue(self):
        """说随机对话"""
        if self.creepy_level > 0.6:
            # 高诡异程度时说邪恶对话
            dialogue = random.choice(BOSS_DIALOGUES['creepy'])
            self.set_mood("creepy", dialogue)
        else:
            # 正常时说闲聊
            dialogue = random.choice(BOSS_DIALOGUES['idle'])
            self.set_mood("neutral", dialogue)
    
    def react_to_choice(self, heart_delta, money_delta):
        """对玩家选择做出反应"""
        if heart_delta < 0:
            # 负面选择 - 开心
            dialogue = random.choice(BOSS_DIALOGUES['happy_negative'])
            if money_delta > 30:
                dialogue = f"{dialogue}\n+${money_delta}!"
            self.set_mood("happy", dialogue)
        elif heart_delta > 0:
            # 正面选择 - 生气
            dialogue = random.choice(BOSS_DIALOGUES['angry_positive'])
            self.set_mood("angry", dialogue)
        else:
            # 中性选择
            self.set_mood("neutral", "Hmm... acceptable.")
    
    def react_to_event(self, event_type):
        """对事件做出反应"""
        if 'complaint' in event_type:
            dialogue = random.choice(BOSS_DIALOGUES['complaint'])
        elif 'inspection' in event_type:
            dialogue = random.choice(BOSS_DIALOGUES['inspector'])
        elif 'warning' in event_type:
            dialogue = random.choice(BOSS_DIALOGUES['warning'])
        else:
            dialogue = "Handle this quickly!"
        self.set_mood("neutral", dialogue)
    
    def update(self, dt, hearts=10, max_hearts=10):
        """更新动画状态"""
        self.pulse += dt * 0.003
        
        # 冷却计时
        if self.click_cooldown > 0:
            self.click_cooldown -= dt
        
        # 自动闲聊计时
        self.idle_timer += dt
        if self.idle_timer > self.idle_chat_interval and self.text_timer <= 0:
            self.idle_timer = 0
            self._say_random_dialogue()  # 每5秒必定说话
        
        # 检测诚信变化并做出反应
        if hearts > self.last_hearts and self.last_hearts <= 5:
            # 诚信恢复了，老板不满
            dialogue = random.choice(BOSS_DIALOGUES['upset_recovery'])
            self.set_mood("angry", dialogue)
        self.last_hearts = hearts
        
        # 根据诚信值计算诡异程度
        self.creepy_level = max(0.0, min(1.0, 1.0 - (hearts / max_hearts)))
        
        # 眼睛跟随鼠标
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.x
        dy = my - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        # 眼睛偏移量随诡异程度增加
        self.eye_offset[0] = (dx / dist) * 8 * (1 + self.creepy_level)
        self.eye_offset[1] = (dy / dist) * 5 * (1 + self.creepy_level)
        
        # 眨眼
        self.blink_timer += dt
        if self.blink_timer > random.randint(2000, 5000):
            self.is_blinking = True
            self.blink_timer = 0
        if self.is_blinking:
            self.blink_timer += dt
            if self.blink_timer > 150:
                self.is_blinking = False
                self.blink_timer = 0
        
        # 诡异状态下的抖动
        if self.creepy_level > 0.5:
            self.shake_amount = random.randint(0, int(5 * self.creepy_level))
        else:
            self.shake_amount = 0
        
        # 更新颜色
        self._update_colors()
        
        # 文字计时
        if self.text_timer > 0:
            self.text_timer -= dt
    
    def _update_colors(self):
        """根据诡异程度更新颜色"""
        # 肤色从温馨的肉色变成苍白/青灰色
        warm_face = (255, 200, 150)
        creepy_face = (180, 180, 200)
        self.face_color = lerp_color(warm_face, creepy_face, self.creepy_level)
        
        # 眼白从白色变成泛黄/血丝
        warm_eye = (255, 255, 255)
        creepy_eye = (255, 240, 220)
        self.eye_color = lerp_color(warm_eye, creepy_eye, self.creepy_level)
        
        # 瞳孔从黑色变成红色
        warm_pupil = (30, 30, 30)
        creepy_pupil = (150, 30, 30)
        self.pupil_color = lerp_color(warm_pupil, creepy_pupil, self.creepy_level)
    
    def set_mood(self, mood, text=""):
        """设置心情和对话"""
        self.mood = mood
        if text:
            self.current_text = text
            self.text_timer = 3000
    
    def draw(self, surf, font=None):
        """绘制食堂老板"""
        x = self.x + random.randint(-self.shake_amount, self.shake_amount)
        y = self.y + random.randint(-self.shake_amount, self.shake_amount)
        
        # 身体/围裙
        self._draw_body(surf, x, y)
        
        # 脸
        self._draw_face(surf, x, y)
        
        # 眼睛
        self._draw_eyes(surf, x, y)
        
        # 嘴巴
        self._draw_mouth(surf, x, y)
        
        # 厨师帽
        self._draw_chef_hat(surf, x, y)
        
        # 对话气泡
        if self.text_timer > 0 and font:
            self._draw_speech(surf, x, y, font)
    
    def _draw_body(self, surf, x, y):
        """绘制身体"""
        # 围裙
        apron_color = lerp_color((255, 255, 255), (200, 180, 180), self.creepy_level)
        body_rect = pygame.Rect(x - 70, y + 50, 140, 180)
        pygame.draw.rect(surf, apron_color, body_rect, border_radius=20)
        
        # 围裙带
        strap_color = lerp_color((100, 150, 100), (80, 60, 60), self.creepy_level)
        pygame.draw.line(surf, strap_color, (x - 35, y + 50), (x - 50, y + 15), 6)
        pygame.draw.line(surf, strap_color, (x + 35, y + 50), (x + 50, y + 15), 6)
    
    def _draw_face(self, surf, x, y):
        """绘制脸部"""
        # 主脸部 - 椭圆形
        face_rect = pygame.Rect(x - 75, y - 85, 150, 170)
        pygame.draw.ellipse(surf, self.face_color, face_rect)
        
        # 脸部轮廓
        outline_color = lerp_color((200, 150, 120), (100, 80, 90), self.creepy_level)
        pygame.draw.ellipse(surf, outline_color, face_rect, 3)
        
        # 腮红（温馨时明显，诡异时消失）
        if self.creepy_level < 0.7:
            blush_alpha = int(100 * (1 - self.creepy_level))
            blush_surf = pygame.Surface((35, 25), pygame.SRCALPHA)
            pygame.draw.ellipse(blush_surf, (255, 150, 150, blush_alpha), (0, 0, 35, 25))
            surf.blit(blush_surf, (x - 60, y + 5))
            surf.blit(blush_surf, (x + 25, y + 5))
    
    def _draw_eyes(self, surf, x, y):
        """绘制眼睛 - 核心的Mr.TomatoS风格效果"""
        eye_y = y - 20
        left_eye_x = x - 30
        right_eye_x = x + 30
        
        # 眼睛大小随诡异程度增大
        eye_size = int(self.eye_size * (1 + self.creepy_level * 0.5))
        pupil_size = int(self.pupil_size * (1 + self.creepy_level * 0.3))
        
        outline_color = lerp_color((200, 150, 120), (100, 80, 90), self.creepy_level)
        
        for ex in [left_eye_x, right_eye_x]:
            # 眼白
            if not self.is_blinking:
                pygame.draw.ellipse(surf, self.eye_color, 
                                   (ex - eye_size//2, eye_y - eye_size//2, eye_size, eye_size))
                
                # 诡异时添加血丝
                if self.creepy_level > 0.5:
                    for _ in range(int(self.creepy_level * 5)):
                        angle = random.random() * math.pi * 2
                        length = random.randint(5, eye_size//2 - 5)
                        ex2 = ex + math.cos(angle) * length
                        ey2 = eye_y + math.sin(angle) * length
                        pygame.draw.line(surf, (200, 100, 100), (ex, eye_y), (int(ex2), int(ey2)), 1)
                
                # 瞳孔 - 跟随鼠标移动
                px = ex + self.eye_offset[0]
                py = eye_y + self.eye_offset[1]
                pygame.draw.circle(surf, self.pupil_color, (int(px), int(py)), pupil_size)
                
                # 高光
                pygame.draw.circle(surf, (255, 255, 255), 
                                  (int(px - pupil_size//3), int(py - pupil_size//3)), 
                                  pupil_size//3)
            else:
                # 闭眼
                pygame.draw.line(surf, outline_color,
                               (ex - eye_size//2, eye_y), (ex + eye_size//2, eye_y), 3)
    
    def _draw_mouth(self, surf, x, y):
        """绘制嘴巴"""
        mouth_y = y + 40
        mouth_width = 50
        
        mouth_color = lerp_color((150, 80, 80), (100, 30, 30), self.creepy_level)
        
        if self.mood == "happy":
            # 微笑
            pygame.draw.arc(surf, mouth_color, 
                          (x - mouth_width//2, mouth_y - 15, mouth_width, 30),
                          math.pi * 0.1, math.pi * 0.9, 4)
        elif self.mood == "angry":
            # 愤怒的嘴
            pygame.draw.line(surf, mouth_color,
                           (x - mouth_width//2, mouth_y + 5),
                           (x + mouth_width//2, mouth_y - 5), 4)
        else:
            # 普通嘴巴
            pygame.draw.line(surf, mouth_color,
                           (x - mouth_width//3, mouth_y),
                           (x + mouth_width//3, mouth_y), 3)
    
    def _draw_chef_hat(self, surf, x, y):
        """绘制厨师帽"""
        hat_color = lerp_color((255, 255, 255), (200, 190, 190), self.creepy_level)
        
        # 帽子主体
        hat_top_y = y - 140
        pygame.draw.ellipse(surf, hat_color, (x - 45, hat_top_y, 90, 70))
        pygame.draw.rect(surf, hat_color, (x - 40, hat_top_y + 35, 80, 35))
        
        # 帽檐
        pygame.draw.rect(surf, hat_color, (x - 50, y - 100, 100, 20), border_radius=5)
        
        # 帽子轮廓
        outline = lerp_color((200, 200, 200), (150, 140, 140), self.creepy_level)
        pygame.draw.ellipse(surf, outline, (x - 45, hat_top_y, 90, 70), 2)
    
    def _draw_speech(self, surf, x, y, font):
        """绘制对话气泡 - 位于老板正上方"""
        # 气泡背景
        text_lines = self.current_text.split('\n')
        max_width = max(font.size(line)[0] for line in text_lines) + 30
        height = len(text_lines) * 28 + 20
        
        # 气泡居中于老板正上方
        bubble_x = x - max_width // 2
        bubble_y = y - 180 - height  # 在厨师帽上方
        
        bubble_color = lerp_color(COLOR_PANEL, COLOR_PANEL_DARK, self.creepy_level)
        text_color = lerp_color(COLOR_TEXT_NORMAL, COLOR_TEXT_CREEPY, self.creepy_level)
        
        # 气泡
        bubble_rect = pygame.Rect(bubble_x, bubble_y, max_width, height)
        pygame.draw.rect(surf, bubble_color, bubble_rect, border_radius=10)
        pygame.draw.rect(surf, text_color, bubble_rect, 2, border_radius=10)
        
        # 气泡尾巴 - 指向下方（老板头顶）
        tail_x = x
        tail_y = bubble_y + height
        pygame.draw.polygon(surf, bubble_color, [
            (tail_x - 10, tail_y),
            (tail_x + 10, tail_y),
            (tail_x, tail_y + 15)
        ])
        pygame.draw.polygon(surf, text_color, [
            (tail_x - 10, tail_y),
            (tail_x + 10, tail_y),
            (tail_x, tail_y + 15)
        ], 2)
        
        # 文字
        for i, line in enumerate(text_lines):
            txt_surf = font.render(line, True, text_color)
            surf.blit(txt_surf, (bubble_x + 15, bubble_y + 10 + i * 28))


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
        self.cash_register = None
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
            # 点击音效 - 优先使用 Videogame Menu BUTTON CLICK
            click_candidates = [
                'Videogame Menu BUTTON CLICK.wav',
                'Button Click 1.wav',
                'Tic Toc Click.wav',
                'click.wav', 'click.ogg', 'select.wav', 'select.ogg'
            ]
            for fn in click_candidates:
                p = os.path.join(sfx_dir, fn)
                if os.path.exists(p):
                    try:
                        self.click = pygame.mixer.Sound(p)
                        print(f"[SoundManager] Loaded click sound: {fn}")
                        break
                    except Exception:
                        self.click = None
            
            # 选择音效 - 使用 Tic Toc Click
            select_candidates = [
                'Tic Toc Click.wav',
                'Button Click 1.wav',
                'select.wav', 'select.ogg'
            ]
            for fn in select_candidates:
                p = os.path.join(sfx_dir, fn)
                if os.path.exists(p):
                    try:
                        self.select = pygame.mixer.Sound(p)
                        print(f"[SoundManager] Loaded select sound: {fn}")
                        break
                    except Exception:
                        self.select = None
            
            # 收银机音效 - 用于老板开心时（赚钱了！）
            cash_candidates = [
                'Cash Register Purchase.wav',
                'old cash register.wav',
                'cash.wav', 'money.wav'
            ]
            for fn in cash_candidates:
                p = os.path.join(sfx_dir, fn)
                if os.path.exists(p):
                    try:
                        self.cash_register = pygame.mixer.Sound(p)
                        print(f"[SoundManager] Loaded cash register sound: {fn}")
                        break
                    except Exception:
                        self.cash_register = None

            # background music: try common names
            bgm_candidates = [
                'bgm_warm.ogg', 'bgm.ogg', 'bgm.mp3', 'bgm.wav', 
                'music.ogg', 'music.mp3'
            ]
            for name in bgm_candidates:
                p = os.path.join(sfx_dir, name)
                if os.path.exists(p):
                    try:
                        self.bgm_path = p
                        print(f"[SoundManager] Found BGM: {name}")
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
    
    def play_cash_register(self):
        """播放收银机音效 - 老板开心时播放"""
        try:
            if not self.available:
                return
            if self.cash_register:
                self.cash_register.play()
        except Exception:
            pass

    def play_bgm(self, loop=True):
        try:
            if not self.available or not self.bgm_path:
                return
            # use mixer.music for streaming bgm
            try:
                pygame.mixer.music.load(self.bgm_path)
                pygame.mixer.music.set_volume(0.5)  # 设置BGM音量为50%
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
    """Button with visual effects based on choice type."""
    def __init__(self, rect, text, font, color=(100,50,140), hover=(240,200,60), bg_image=None, effect_type="neutral", icon_image=None):
        super().__init__(rect, text, font, color=color, hover=hover)
        self.scale = 1.0
        self.target_scale = 1.0
        self.pressed = False
        self.bg_image = bg_image
        self.icon_image = icon_image  # 图标图片
        self.effect_type = effect_type  # "negative", "positive", "neutral"
        self.pulse = 0
        
        # 根据效果类型设置颜色
        if effect_type == "negative":
            self.base_color = (180, 60, 60)  # 红色 - 负面
            self.hover_color = (220, 80, 80)
            self.icon = "-"  # 负面图标
        elif effect_type == "positive":
            self.base_color = (60, 150, 80)  # 绿色 - 正面
            self.hover_color = (80, 180, 100)
            self.icon = "+"  # 正面图标
        else:
            self.base_color = (100, 100, 120)  # 灰色 - 中性
            self.hover_color = (130, 130, 150)
            self.icon = "~"

    def draw(self, surf):
        mpos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mpos)
        
        # 脉冲动画
        self.pulse += 0.1
        pulse_offset = math.sin(self.pulse) * 2 if hovered else 0
        
        if hovered:
            self.target_scale = 1.05
        else:
            self.target_scale = 1.0

        # smooth approach to target scale
        if self.scale < self.target_scale:
            self.scale = min(self.scale + 0.04, self.target_scale)
        elif self.scale > self.target_scale:
            self.scale = max(self.scale - 0.04, self.target_scale)

        # compute scaled rect centered on original rect center
        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        cx, cy = self.rect.center
        draw_rect = pygame.Rect(0, 0, w, h)
        draw_rect.center = (cx, int(cy + pulse_offset))

        # 绘制按钮背景
        if getattr(self, 'bg_image', None):
            try:
                bi = pygame.transform.smoothscale(self.bg_image, (draw_rect.width, draw_rect.height))
                surf.blit(bi, draw_rect.topleft)
            except Exception:
                c = self.hover_color if hovered else self.base_color
                pygame.draw.rect(surf, c, draw_rect, border_radius=10)
        else:
            c = self.hover_color if hovered else self.base_color
            pygame.draw.rect(surf, c, draw_rect, border_radius=10)
            
            # 添加边框
            border_color = (255, 255, 255) if hovered else (180, 180, 180)
            pygame.draw.rect(surf, border_color, draw_rect, 2, border_radius=10)
        
        # 绘制图标在左侧
        icon_x = draw_rect.x + 8
        icon_y = draw_rect.centery
        
        if self.icon_image:
            # 使用图标图片
            icon_size = min(draw_rect.height - 8, 48)
            try:
                scaled_icon = pygame.transform.smoothscale(self.icon_image, (icon_size, icon_size))
                surf.blit(scaled_icon, (icon_x, icon_y - icon_size // 2))
                icon_x += icon_size + 4
            except Exception:
                pass
        else:
            # 使用文字图标
            icon_font = load_font("assets/fonts/m6x11.ttf", 28)
            if self.effect_type == "negative":
                icon_color = (255, 100, 100)
                icon_text = "-"
            elif self.effect_type == "positive":
                icon_color = (100, 255, 100)
                icon_text = "+"
            else:
                icon_color = (200, 200, 200)
                icon_text = "~"
            
            icon_surf = icon_font.render(icon_text, True, icon_color)
            surf.blit(icon_surf, (icon_x, icon_y - icon_surf.get_height() // 2))
            icon_x += icon_surf.get_width() + 4

        # 绘制文本（图标右边）- 根据效果类型设置易读深色
        if self.effect_type == "negative":
            text_color = (80, 20, 20)  # 深红色
        elif self.effect_type == "positive":
            text_color = (20, 60, 20)  # 深绿色
        else:
            text_color = (40, 40, 40)  # 深灰色
        txt = self.font.render(self.text, True, text_color)
        text_x = icon_x + (draw_rect.right - icon_x) // 2
        text_y = draw_rect.centery
        surf.blit(txt, txt.get_rect(center=(text_x, text_y)))

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
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 56)
        self.subtitle_font = load_font("assets/fonts/m6x11.ttf", 28)
        # increase button font size for better visibility on title screen
        self.btn_font = load_font("assets/fonts/m6x11.ttf", 36)
        # use the JPG background for the title screen explicitly
        self.bg = load_image(os.path.join('assets', 'ui', 'PICTURE_background.jpg'), (WINDOW_WIDTH, WINDOW_HEIGHT))
        # change Start/Quit button base color to #e5002b
        btn_color = (229, 0, 43)
        btn_hover = (255, 60, 80)
        # button rects - 右侧区域，不与老板重叠
        start_rect = (WINDOW_WIDTH//2 + 80, 350, 320, 60)
        archive_rect = (WINDOW_WIDTH//2 + 80, 430, 320, 60)  # 档案馆按钮
        quit_rect = (WINDOW_WIDTH//2 + 80, 510, 320, 60)
        self.start_btn = Button(start_rect, "Start Game", self.btn_font, color=btn_color, hover=btn_hover)
        self.archive_btn = Button(archive_rect, "Archive", self.btn_font, color=btn_color, hover=btn_hover)
        self.quit_btn = Button(quit_rect, "Quit", self.btn_font, color=btn_color, hover=btn_hover)
        
        # 标题界面的预览老板 - 左侧居中
        self.preview_boss = CanteenBoss(250, WINDOW_HEIGHT // 2 + 30, 180)
        self.preview_boss.mood = "happy"

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
            if self.archive_btn.handle_event(e):
                try:
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                self.game.change_scene('archive')
            if self.quit_btn.handle_event(e):
                try:
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                pygame.quit(); sys.exit()

    def render(self, surf):
        # ==================== Mr.TomatoS风格: 温馨背景 ====================
        surf.fill(COLOR_BG_WARM)
        
        # 条纹背景效果
        stripe_width = 60
        for i in range(WINDOW_WIDTH // stripe_width + 2):
            x = i * stripe_width
            color = (255, 245, 225) if i % 2 == 0 else (250, 240, 215)
            pygame.draw.rect(surf, color, (x, 0, stripe_width, WINDOW_HEIGHT))
        
        # 尝试叠加原背景图
        try:
            if self.bg:
                self.bg.set_alpha(180)
                surf.blit(self.bg, (0, 0))
        except Exception:
            pass
        
        # ==================== Mr.TomatoS风格: 绘制预览老板 ====================
        self.preview_boss.update(16, 10, 10)  # 温馨状态
        preview_font = load_font("assets/fonts/m6x11.ttf", 20)
        self.preview_boss.draw(surf, preview_font)
        
        # 标题已删除 - 只保留老板和按钮
        
        # draw Start/Archive/Quit buttons
        if getattr(self, 'start_img', None):
            surf.blit(self.start_img, self.start_btn.rect.topleft)
            txt = self.btn_font.render(self.start_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.start_btn.rect.center))
        else:
            self.start_btn.draw(surf)
            txt = self.btn_font.render(self.start_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.start_btn.rect.center))

        # Archive button - 与Start统一风格
        if getattr(self, 'start_img', None):
            surf.blit(self.start_img, self.archive_btn.rect.topleft)
            txt = self.btn_font.render(self.archive_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.archive_btn.rect.center))
        else:
            self.archive_btn.draw(surf)
            txt = self.btn_font.render(self.archive_btn.text, True, (185,12,12))
            surf.blit(txt, txt.get_rect(center=self.archive_btn.rect.center))

        if getattr(self, 'quit_img', None):
            surf.blit(self.quit_img, self.quit_btn.rect.topleft)
            txt = self.btn_font.render(self.quit_btn.text, True, (255,255,255))
            surf.blit(txt, txt.get_rect(center=self.quit_btn.rect.center))
        else:
            self.quit_btn.draw(surf)
            txt = self.btn_font.render(self.quit_btn.text, True, (255,255,255))
            surf.blit(txt, txt.get_rect(center=self.quit_btn.rect.center))
        
        # 风格说明
        style_font = load_font("assets/fonts/m6x11.ttf", 18)
        style_text = "Inspired by Mr.TomatoS"
        style_surf = style_font.render(style_text, True, (150, 150, 150))
        surf.blit(style_surf, (20, WINDOW_HEIGHT - 30))


class ArchiveScene(SceneBase):
    """档案馆场景 - 显示所有结局，未解锁的显示灰色问号"""
    def __init__(self, game):
        super().__init__(game)
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 48)
        self.font = load_font("assets/fonts/m6x11.ttf", 24)
        self.small_font = load_font("assets/fonts/m6x11.ttf", 18)
        
        # 返回按钮
        btn_color = (100, 80, 140)
        btn_hover = (140, 120, 180)
        self.back_btn = Button((50, WINDOW_HEIGHT - 80, 200, 50), "Back", self.font, color=btn_color, hover=btn_hover)
        
        # 结局卡片布局
        self.card_width = 220
        self.card_height = 280
        self.card_spacing = 30
        
    def start(self):
        # 每次进入时刷新已解锁结局
        self.unlocked = get_unlocked_endings()
        
    def handle_events(self, events):
        for e in events:
            if self.back_btn.handle_event(e):
                try:
                    if getattr(self.game, 'sound', None):
                        self.game.sound.play_click()
                except Exception:
                    pass
                self.game.change_scene('title')
                
    def render(self, surf):
        # 深色背景
        surf.fill((30, 25, 35))
        
        # 标题
        title_text = "ARCHIVE"
        title_surf = self.title_font.render(title_text, True, (200, 180, 220))
        surf.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 60)))
        
        # 副标题
        sub_text = "Endings Collection"
        sub_surf = self.font.render(sub_text, True, (150, 140, 160))
        surf.blit(sub_surf, sub_surf.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        
        # 已解锁数量
        unlocked_count = len(self.unlocked) if hasattr(self, 'unlocked') else 0
        total_count = len(ALL_ENDINGS)
        count_text = f"Unlocked: {unlocked_count}/{total_count}"
        count_surf = self.small_font.render(count_text, True, (120, 110, 130))
        surf.blit(count_surf, count_surf.get_rect(center=(WINDOW_WIDTH // 2, 130)))
        
        # 绘制结局卡片
        endings_list = list(ALL_ENDINGS.items())
        total_width = len(endings_list) * self.card_width + (len(endings_list) - 1) * self.card_spacing
        start_x = (WINDOW_WIDTH - total_width) // 2
        card_y = 170
        
        for idx, (key, info) in enumerate(endings_list):
            card_x = start_x + idx * (self.card_width + self.card_spacing)
            is_unlocked = key in (self.unlocked if hasattr(self, 'unlocked') else [])
            
            self._draw_ending_card(surf, card_x, card_y, key, info, is_unlocked)
        
        # 返回按钮
        self.back_btn.draw(surf)
        txt = self.font.render(self.back_btn.text, True, (220, 200, 255))
        surf.blit(txt, txt.get_rect(center=self.back_btn.rect.center))
        
    def _draw_ending_card(self, surf, x, y, key, info, is_unlocked):
        """绘制单个结局卡片"""
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        
        if is_unlocked:
            # 已解锁 - 显示结局信息
            bg_color = (50, 45, 60)
            border_color = info['color']
            
            # 卡片背景
            pygame.draw.rect(surf, bg_color, card_rect, border_radius=12)
            pygame.draw.rect(surf, border_color, card_rect, 3, border_radius=12)
            
            # 尝试加载结局图片
            ending_filename_map = {
                'spiral': 'ending_spiral.png',
                '1A': 'ending_1A.png',
                '1B': 'ending_1B.png',
                'best_red': 'ending_1B.png',
                'apathy': 'ending_apathy.png',
            }
            fname = ending_filename_map.get(key, f'ending_{key}.png')
            ending_png = os.path.join('assets', 'ui', fname)
            
            # 图片区域
            img_rect = pygame.Rect(x + 10, y + 10, self.card_width - 20, 120)
            if os.path.exists(ending_png):
                try:
                    img = load_image(ending_png, (img_rect.width, img_rect.height))
                    surf.blit(img, img_rect.topleft)
                except Exception:
                    pygame.draw.rect(surf, (40, 35, 50), img_rect, border_radius=8)
            else:
                pygame.draw.rect(surf, (40, 35, 50), img_rect, border_radius=8)
            
            # 结局名称
            name_text = info['name']
            # 自动换行
            words = name_text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if self.small_font.size(test_line)[0] <= self.card_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            name_y = y + 140
            for line in lines[:2]:  # 最多2行
                name_surf = self.small_font.render(line, True, info['color'])
                surf.blit(name_surf, name_surf.get_rect(center=(x + self.card_width // 2, name_y)))
                name_y += 22
            
            # 描述
            desc_text = info['description']
            desc_lines = []
            current_line = ""
            for word in desc_text.split():
                test_line = current_line + " " + word if current_line else word
                if self.small_font.size(test_line)[0] <= self.card_width - 20:
                    current_line = test_line
                else:
                    if current_line:
                        desc_lines.append(current_line)
                    current_line = word
            if current_line:
                desc_lines.append(current_line)
            
            desc_y = y + 195
            for line in desc_lines[:3]:  # 最多3行
                desc_surf = self.small_font.render(line, True, (160, 150, 170))
                surf.blit(desc_surf, desc_surf.get_rect(center=(x + self.card_width // 2, desc_y)))
                desc_y += 20
                
        else:
            # 未解锁 - 显示灰色问号
            bg_color = (40, 38, 45)
            border_color = (80, 75, 90)
            
            # 卡片背景
            pygame.draw.rect(surf, bg_color, card_rect, border_radius=12)
            pygame.draw.rect(surf, border_color, card_rect, 2, border_radius=12)
            
            # 大问号
            question_font = load_font("assets/fonts/m6x11plus.ttf", 80)
            question_surf = question_font.render("?", True, (70, 65, 80))
            surf.blit(question_surf, question_surf.get_rect(center=(x + self.card_width // 2, y + 100)))
            
            # 锁定文本
            locked_text = "LOCKED"
            locked_surf = self.font.render(locked_text, True, (90, 85, 100))
            surf.blit(locked_surf, locked_surf.get_rect(center=(x + self.card_width // 2, y + 200)))
            
            # 提示
            hint_text = "Play to unlock"
            hint_surf = self.small_font.render(hint_text, True, (70, 65, 80))
            surf.blit(hint_surf, hint_surf.get_rect(center=(x + self.card_width // 2, y + 240)))


class PrepScene(SceneBase):
    def __init__(self, game):
        super().__init__(game)
        self.font = load_font("assets/fonts/m6x11.ttf", 22)
        # title font for centered stage heading
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 40)
        # prepare 2x2 grid - 缩小按钮尺寸避免重叠
        btn_w = 320
        btn_h = 80
        spacing = 20
        # (text, heart_delta, money_delta, icon_name)
        self.options = [
            ("Use expired ingredients", -2, +50, "opt_expired.png"),
            ("Ignore insect bodies", -1, +30, "opt_insect.png"),
            ("Ignore dirty utensils", -1, +20, "opt_dirty_utensils.png"),
            ("Clean thoroughly", 0, -80, "opt_clean.png"),
        ]
        self.buttons = []
        grid_w = btn_w * 2 + spacing
        grid_h = btn_h * 2 + spacing
        # 右侧区域放置按钮，左侧放老板
        start_x = 480
        start_y = 200
        # try to use a provided button art for prep options
        try:
            prep_btn_path = os.path.join('assets', 'ui', 'PICTURE_button1.png')
            prep_btn_img = load_image(prep_btn_path) if os.path.exists(prep_btn_path) else None
        except Exception:
            prep_btn_img = None

        for idx, (t, v, m, icon_name) in enumerate(self.options):
            col = idx % 2
            row = idx // 2
            x = start_x + col * (btn_w + spacing)
            y = start_y + row * (btn_h + spacing)
            rect = (x, y, btn_w, btn_h)
            # 根据heart_delta确定效果类型
            if v < 0:
                eff_type = "negative"
            elif v > 0:
                eff_type = "positive"
            else:
                eff_type = "neutral" if m < 0 else "positive"  # 无心变化但花钱算中性/正面
            # 加载图标
            icon_img = None
            try:
                icon_path = os.path.join('assets', 'ui', 'icons', icon_name)
                if os.path.exists(icon_path):
                    icon_img = load_image(icon_path)
            except Exception:
                pass
            self.buttons.append(AnimatedButton(rect, t, self.font, color=(100,50,140), hover=(240,200,60), bg_image=prep_btn_img, effect_type=eff_type, icon_image=icon_img))

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

            # 检查是否点击了老板
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hasattr(self, 'boss') and self.boss.handle_click(e.pos):
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
                    
                    # 让老板对选择做出反应
                    if hasattr(self, 'boss'):
                        self.boss.react_to_choice(heart_delta, money_delta)
                    
                    # 负面选择时播放收银机音效（老板开心赚钱了）
                    if heart_delta < 0:
                        try:
                            if getattr(self.game, 'sound', None):
                                self.game.sound.play_cash_register()
                        except Exception:
                            pass
                    
                    self.game.change_hearts(heart_delta)
                    self.game.change_money(money_delta)
                    self.game.add_log(f"Prep choice: {self.options[i][0]} (money {money_delta:+d})")
                    # proceed to business after a choice
                    self.game.change_scene('business')

    def render(self, surf):
        # ==================== Mr.TomatoS风格: 渐变背景 ====================
        creepy_level = max(0.0, min(1.0, 1.0 - (self.game.hearts / 10)))
        bg_color = lerp_color(COLOR_BG_WARM, COLOR_BG_CREEPY, creepy_level)
        surf.fill(bg_color)
        
        # 条纹背景效果
        stripe_color1 = lerp_color((255, 240, 220), (50, 30, 40), creepy_level)
        stripe_color2 = lerp_color((250, 235, 215), (40, 20, 30), creepy_level)
        stripe_width = 60
        for i in range(WINDOW_WIDTH // stripe_width + 2):
            x = i * stripe_width
            color = stripe_color1 if i % 2 == 0 else stripe_color2
            pygame.draw.rect(surf, color, (x, 0, stripe_width, WINDOW_HEIGHT))
        
        # 尝试叠加原背景图
        try:
            if getattr(self, 'bg', None):
                self.bg.set_alpha(int(180 * (1 - creepy_level * 0.5)))
                surf.blit(self.bg, (0, 0))
        except Exception:
            pass
        
        # ==================== Mr.TomatoS风格: 绘制食堂老板 ====================
        # 老板固定在左侧
        if hasattr(self.game, 'boss'):
            self.game.boss.x = 200
            self.game.boss.y = WINDOW_HEIGHT // 2 + 50
            self.game.boss.update(16, self.game.hearts, 10)
            boss_font = load_font("assets/fonts/m6x11.ttf", 20)
            self.game.boss.draw(surf, boss_font)
        
        # 标题在右上方
        title_text = 'Preparation Phase'
        title_pos = (750, 80)
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
        # 字体 - 适当缩小以适应按钮
        self.font = load_font("assets/fonts/m6x11.ttf", 20)
        # centered title font
        self.title_font = load_font("assets/fonts/m6x11plus.ttf", 36)
        # (text, heart_delta, money_delta, icon_name) - 简化文本
        self.action_opts = [
            ("Ignore cockroaches", -1, +30, "opt_cockroach.png"),
            ("Use dirty plates", -1, +40, "opt_dirty_plate.png"),
            ("Small portions", -1, +20, "opt_small_portion.png"),
            ("Serve wrong dish", 0, -10, "opt_wrong_dish.png"),
            ("Serve quality food", 0, -10, "opt_quality.png"),
        ]
        # create 2x2 grid + 1 row for last item
        self.buttons = []
        btn_w = 280
        btn_h = 70
        spacing = 15
        cols = 2
        rows = (len(self.action_opts) + cols - 1) // cols
        grid_w = btn_w * cols + spacing
        grid_h = btn_h * rows + spacing * (rows - 1)
        # 右侧区域放置按钮
        start_x = 500
        start_y = 180
        # load per-option button art: first four use PICTURE_button2.png, last (long) uses PICTURE_button3.png
        try:
            pic2_path = os.path.join('assets', 'ui', 'PICTURE_button2.png')
            pic3_path = os.path.join('assets', 'ui', 'PICTURE_button3.png')
            pic2 = load_image(pic2_path) if os.path.exists(pic2_path) else None
            pic3 = load_image(pic3_path) if os.path.exists(pic3_path) else None
        except Exception:
            pic2 = None
            pic3 = None

        for idx, (t, v, m, icon_name) in enumerate(self.action_opts):
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
            # 根据heart_delta确定效果类型
            if v < 0:
                eff_type = "negative"
            elif v > 0:
                eff_type = "positive"
            else:
                eff_type = "neutral" if m <= 0 else "positive"
            # 加载图标
            icon_img = None
            try:
                icon_path = os.path.join('assets', 'ui', 'icons', icon_name)
                if os.path.exists(icon_path):
                    icon_img = load_image(icon_path)
            except Exception:
                pass
            self.buttons.append(AnimatedButton(rect, t, self.font, color=(100,50,140), hover=(240,200,60), bg_image=bg, effect_type=eff_type, icon_image=icon_img))

        # Event/triggers
        self.event_queue = ["complaint1", "inspection1", "inspection2", "complaint2", "warning"]
        random.shuffle(self.event_queue)
        self.ticks = 0
        self.event_timer = 0
        self.current_event = None
        # event timing: balanced for gameplay
        # values in milliseconds
        self.event_delay_min = 8000   # 8 seconds
        self.event_delay_max = 15000  # 15 seconds
        self.next_event_delay = random.randint(self.event_delay_min, self.event_delay_max)
        # prepare two interactive buttons for event choices (stacked vertically when shown)
        # placeholders; rects will be positioned during render
        # Choice A通常是负面选择（逃避/贿赂），Choice B是正面选择（道歉/承担责任）
        self.event_buttons = [AnimatedButton((0,0,300,64), 'Choice A', self.font, color=(100,60,60), hover=(160,100,100), effect_type="negative"),
                              AnimatedButton((0,0,300,64), 'Choice B', self.font, color=(60,100,60), hover=(100,160,100), effect_type="positive")]
        # map events to (main_text, choiceA_text, choiceB_text, icon_name)
        self.event_texts = {
            'complaint1': ("A student is complaining loudly.", 'Brush off', 'Apologize & compensate', 'event_complaint.png'),
            'inspection1': ("A health inspector appears.", 'Bribe', 'Accept inspection', 'event_inspector.png'),
            'inspection2': ("Another inspector finds issues.", 'Fire temp', 'Take responsibility', 'event_inspector.png'),
            'complaint2': ("Another complaint arrives.", 'Dodge', 'Apologize', 'event_complaint.png'),
            'warning': ("The school sent a warning.", 'Ignore & continue', 'Fix sanitation', 'event_warning.png'),
        }
        # 加载事件图标
        self.event_icons = {}
        for event_key, event_data in self.event_texts.items():
            if len(event_data) >= 4:
                icon_name = event_data[3]
                try:
                    icon_path = os.path.join('assets', 'ui', 'icons', icon_name)
                    if os.path.exists(icon_path):
                        self.event_icons[event_key] = load_image(icon_path)
                except Exception:
                    pass
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

            # 检查是否点击了老板
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hasattr(self, 'boss') and self.boss.handle_click(e.pos):
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
                    
                    # 让老板对选择做出反应
                    if hasattr(self, 'boss'):
                        self.boss.react_to_choice(heart_delta, money_delta)
                    
                    # 负面选择时播放收银机音效（老板开心赚钱了）
                    if heart_delta < 0:
                        try:
                            if getattr(self.game, 'sound', None):
                                self.game.sound.play_cash_register()
                        except Exception:
                            pass
                    
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

                    # trigger the first event after 4 actions
                    if not self.first_event_triggered and self.actions_done >= 4 and self.event_queue:
                        self.current_event = self.event_queue.pop(0)
                        self.first_event_triggered = True
                        # 让老板对事件做出反应
                        if hasattr(self, 'boss'):
                            self.boss.react_to_event(self.current_event)

    def resolve_event(self, ev, choice):
        # Apply heart changes according to design
        if ev == 'complaint1':
            if choice == 'A':
                ah = self.apply_heart(-2)
                self.game.add_log(f'You dodge the complaint. (hearts {ah:+d})')
                # 老板对负面选择表示赞同
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(-2, 0)
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
                # 老板对正面选择表示不满
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(+2, -50)
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
                # 老板对行贿选择表示赞同
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(-3, -200)
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
                # 老板对接受检查表示不满
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(0, -50)
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
                # 老板对甩锅选择表示赞同
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(-2, 0)
                try:
                    if self.game.hearts <= 3:
                        self.game.history['post_black_negative_consec'] = self.game.history.get('post_black_negative_consec', 0) + 1
                        self.game.history['last_negative_choice_money'] = self.game.money
                except Exception:
                    pass
            else:
                ah = self.apply_heart(+1)
                self.game.add_log(f'You accept responsibility. (hearts {ah:+d})')
                # 老板对承担责任表示不满
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(+1, 0)
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
                # 老板对推卸投诉表示赞同
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(-1, 0)
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
                # 老板对道歉补偿表示不满
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(+1, -30)
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
                # 老板对无视警告表示赞同（虽然疯狂）
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(-999, 0)
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
                # 老板对接受整改表示不满
                if hasattr(self, 'boss'):
                    self.boss.react_to_choice(+1, 0)
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
        # ==================== Mr.TomatoS风格: 渐变背景 ====================
        creepy_level = max(0.0, min(1.0, 1.0 - (self.game.hearts / 10)))
        bg_color = lerp_color(COLOR_BG_WARM, COLOR_BG_CREEPY, creepy_level)
        surf.fill(bg_color)
        
        # 条纹背景效果
        stripe_color1 = lerp_color((255, 240, 220), (50, 30, 40), creepy_level)
        stripe_color2 = lerp_color((250, 235, 215), (40, 20, 30), creepy_level)
        stripe_width = 60
        for i in range(WINDOW_WIDTH // stripe_width + 2):
            x = i * stripe_width
            color = stripe_color1 if i % 2 == 0 else stripe_color2
            pygame.draw.rect(surf, color, (x, 0, stripe_width, WINDOW_HEIGHT))
        
        # 尝试叠加原背景图
        try:
            if getattr(self, 'bg', None):
                self.bg.set_alpha(int(150 * (1 - creepy_level * 0.6)))
                surf.blit(self.bg, (0, 0))
        except Exception:
            pass
        
        # 静态噪点效果 (高诡异程度时)
        if creepy_level > 0.6:
            static_alpha = int(30 * (creepy_level - 0.6) / 0.4)
            static_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            for _ in range(300):
                sx = random.randint(0, WINDOW_WIDTH)
                sy = random.randint(0, WINDOW_HEIGHT)
                c = random.randint(0, 255)
                pygame.draw.rect(static_surf, (c, c, c, static_alpha), (sx, sy, 2, 2))
            surf.blit(static_surf, (0, 0))
        
        # ==================== Mr.TomatoS风格: 绘制食堂老板 ====================
        # 老板固定在左侧
        if hasattr(self.game, 'boss'):
            self.game.boss.x = 200
            self.game.boss.y = WINDOW_HEIGHT // 2 + 50
            self.game.boss.update(16, self.game.hearts, 10)
            boss_font = load_font("assets/fonts/m6x11.ttf", 20)
            self.game.boss.draw(surf, boss_font)
        
        # 标题在右上方
        title_y = 80
        title_text = "Business Hours"
        title_pos = (750, title_y)
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
            # split main event description and two choice labels (ignore 4th element if present)
            event_data = self.event_texts.get(self.current_event, ('', 'Choice A', 'Choice B', ''))
            main_text, a_text, b_text = event_data[0], event_data[1], event_data[2]
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
            
            # 绘制事件图标（如果有）
            event_icon = self.event_icons.get(self.current_event)
            icon_offset = 0
            if event_icon:
                icon_size = 80
                try:
                    scaled_icon = pygame.transform.smoothscale(event_icon, (icon_size, icon_size))
                    icon_x = content_x
                    icon_y = ey + top_pad + 20
                    surf.blit(scaled_icon, (icon_x, icon_y))
                    icon_offset = icon_size + 15  # 文本偏移
                except Exception:
                    pass
            
            wrapped = wrap_text(main_text, text_font, content_w - icon_offset)
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
                surf.blit(txt_surf, (content_x + icon_offset, text_start_y + i * line_h))

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

        # 解锁当前结局
        if hasattr(self, 'key') and self.key:
            unlock_ending(self.key)

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
        pygame.display.set_caption('Evil Canteen Simulator - 黑心食堂模拟器')
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
        
        # ==================== Mr.TomatoS风格: 食堂老板角色 ====================
        self.boss = CanteenBoss(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2 + 30)
        self.history['post_black_increased'] = False
        # consecutive negative event choices after black
        self.history['post_black_negative_consec'] = 0
        # record last money value when a negative event choice occurred after black
        self.history['last_negative_choice_money'] = 0
        self.logs = []

        # scenes
        self.scenes = {
            'title': TitleScene(self),
            'archive': ArchiveScene(self),
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

        # ==================== Mr.TomatoS风格: 老板反应 ====================
        # 注意：这是黑心老板！负面选择会让他开心，正面选择会让他不开心
        if hasattr(self, 'boss'):
            if delta < 0:
                # 负面选择 - 黑心老板开心（省钱了）
                if self.hearts <= 3:
                    self.boss.set_mood("happy", "Excellent choice!")
                else:
                    self.boss.set_mood("happy", "Good... save money!")
            elif delta > 0:
                # 正面选择 - 黑心老板不开心（花钱了）
                self.boss.set_mood("angry", "Waste of money!")
            else:
                self.boss.set_mood("neutral", "Hmm...")

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
        # show last 3 logs in bottom-left (simplified)
        if not self.logs:
            return
        font = load_font("assets/fonts/m6x11.ttf", 16)
        lines = self.logs[-3:]
        padding = 6
        line_h = 18
        box_w = 400
        box_h = padding*2 + line_h * len(lines)
        x = 10
        y = WINDOW_HEIGHT - box_h - 10
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 150))
        for i, l in enumerate(lines):
            # 截断过长的文本
            display_text = l[:50] + "..." if len(l) > 50 else l
            txt = font.render(display_text, True, (220, 220, 220))
            box.blit(txt, (padding, padding + i * line_h))
        surf.blit(box, (x, y))

    def draw_debug(self, surf):
        # 移除debug面板 - 简化UI
        pass
    
    def draw_money(self, surf):
        # deprecated: draw_money replaced by draw_status (kept for compatibility)
        pass

    def draw_status(self, surf):
        """Draw a compact status box at top-right containing hearts and money.
        Money is right-aligned with $ prefix and colored green (profit) or red (loss).
        """
        # 紧凑的状态面板
        box_w = 280
        box_h = 80
        padding = 10
        x = WINDOW_WIDTH - box_w - 15
        y = 15
        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        pygame.draw.rect(panel, (100, 100, 100), (0, 0, box_w, box_h), 2, border_radius=8)

        # hearts: 简化显示
        max_hearts = self.heart_bar.max
        heart_size = 20
        spacing = 24
        total_row_w = heart_size + spacing * (max_hearts - 1)
        start_x = (box_w - total_row_w) // 2
        heart_y = 12
        self.heart_bar.draw(panel, self.hearts, x=start_x, y=heart_y, size=heart_size, spacing=spacing)

        # money text
        font = load_font("assets/fonts/m6x11.ttf", 28)
        money_text = f"${self.money:+d}"
        color = (80, 220, 100) if self.money >= 0 else (220, 80, 80)
        txt = font.render(money_text, True, color)
        money_x = (box_w - txt.get_width()) // 2
        money_y = heart_y + heart_size + 10
        panel.blit(txt, (money_x, money_y))

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



