"""
The Evil Canteen Simulator — Demo
运行：在终端输入 `python main.py`
注：适合 Python 新手。界面使用纯 Pygame 绘制，无外部图片/音频依赖。
"""

import pygame
import sys
import random
from pygame.locals import *

# ---------- 基本设置 ----------
pygame.init()
WIDTH, HEIGHT = 960, 640
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Evil Canteen Simulator — Demo")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 18)
BIGFONT = pygame.font.SysFont("Arial", 28)

# ---------- 颜色 ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK = (40, 40, 40)
YELLOW = (235, 200, 80)
GREEN = (100, 200, 120)
RED = (220, 60, 60)

# ---------- 游戏状态 ----------
state = {
    "money": 500,
    "evilness": 0,    # 黑心值（越高越“黑心”）
    "hygiene": 100,   # 卫生指数（0-100）
    "day": 1,
    "reviews": [],    # 列表，存储差评字典
    "messages": [],   # 屏幕上的弹窗（短消息）
    "ended": False,
    "slogan": "",     # 玩家可输入的文本（示例）
    "typing": False
}

MAX_DAYS = 7  # demo 游戏天数（可修改）


# ---------- UI 元件帮助函数 ----------
def draw_text(surface, text, pos, font=FONT, color=BLACK):
    txt = font.render(text, True, color)
    surface.blit(txt, pos)

def push_message(text, ttl=180):
    """在屏幕上显示短消息（ttl 帧后消失）"""
    state["messages"].append({"text": text, "ttl": ttl})

# ---------- 简易按钮类 ----------
class Button:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.hover = False

    def draw(self, surf):
        color = (180, 90, 30) if self.hover else (150, 70, 20)
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        draw_text(surf, self.label, (self.rect.x + 8, self.rect.y + 6), FONT, WHITE)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ---------- 创建按钮（右侧操作） ----------
buttons = [
    Button((720, 120, 200, 40), "Raise price ↑"),
    Button((720, 180, 200, 40), "Use pre-made meal"),
    Button((720, 240, 200, 40), "Delete negative review"),
    Button((720, 300, 200, 40), "PR campaign (type slogan)")
]

# ---------- 游戏逻辑函数 ----------
def next_day():
    """执行一天结束后的结算与事件，然后推进天数"""
    # 收入来自：基础收入 + 顾客数量（受卫生和价格影响）
    base_income = 120
    price_factor = 1 + (state["evilness"] / 200)  # 黑心越高，能涨价（荒谬）
    hygiene_penalty = max(0.4, state["hygiene"] / 120)
    income = int(base_income * price_factor * hygiene_penalty)
    state["money"] += income

    # 随机事件
    roll = random.random()
    if roll < 0.12:
        # 发现异物
        state["evilness"] += 12
        state["hygiene"] -= 25
        push_message("Alert: Student found a cockroach in the meal! (+12 evilness)")
    elif roll < 0.25:
        # 负面小爆发
        bad = random.choice([
            "Local blogger posts a bad review.",
            "Several students got mild food poisoning.",
            "A student live-streams the greasy food."
        ])
        state["evilness"] += 8
        state["hygiene"] -= 10
        state["reviews"].append({"text": bad, "severity": random.randint(1, 3)})
        push_message("Incident: " + bad)
    elif roll < 0.33:
        # 政策抽查
        if state["hygiene"] < 40:
            # 被罚款
            fine = 80
            state["money"] = max(0, state["money"] - fine)
            push_message("Health inspection failed! Fine imposed.")
            state["evilness"] += 5
        else:
            push_message("Health inspection passed (lucky).")

    # 每天小幅恢复或恶化
    state["hygiene"] = max(0, min(100, state["hygiene"] + random.randint(-3, 3)))

    state["day"] += 1
    if state["day"] > MAX_DAYS or state["evilness"] >= 120:
        end_game()

def end_game():
    state["ended"] = True
    # 生成结局信息
    e = state["evilness"]
    if e <= 30:
        state["ending_text"] = "Conscience wins. You kept the canteen honest."
    elif e <= 70:
        state["ending_text"] = "You balanced profit and... some complaints. Medium success."
    elif e <= 100:
        state["ending_text"] = "You made a killing. Local news calls you 'Black Heart Manager'."
    else:
        state["ending_text"] = "You are recruited by the national chain — the King of Black Canteens."

# ---------- 响应按钮逻辑 ----------
def handle_action(idx):
    if idx == 0:  # Raise price
        state["money"] += 40
        state["evilness"] += 6
        state["hygiene"] -= 2
        push_message("You raised prices. Students grumble.")
    elif idx == 1:  # Use pre-made meal
        state["money"] += 90
        state["evilness"] += 12
        state["hygiene"] -= 18
        push_message("Pre-made meal introduced. Profit up, hygiene down.")
    elif idx == 2:  # Delete negative review
        if state["reviews"]:
            removed = state["reviews"].pop(0)
            state["evilness"] += 4
            push_message("A review was deleted. You bought silence.")
        else:
            push_message("No negative reviews to delete.")
    elif idx == 3:  # PR campaign -> 开始文本输入
        state["typing"] = True
        state["slogan"] = ""
        push_message("Type your PR slogan and press Enter.")


# ---------- 绘制餐厅场景（简易程序化美术） ----------
def draw_canteen(surf):
    # 背景色根据 evilness 变化（越高越油腻）
    e = min(120, state["evilness"])
    t = e / 120
    # interpolate between light green and sick yellow-green
    bg = (
        int((1 - t) * 180 + t * 220),
        int((1 - t) * 220 + t * 200),
        int((1 - t) * 200 + t * 140)
    )
    surf.fill(bg)

    # 上方食堂板
    pygame.draw.rect(surf, (200, 180, 140), (80, 60, 560, 160), border_radius=8)
    draw_text(surf, "School Canteen — Today's Special: Mystery Meal", (100, 70), BIGFONT)

    # 桌面油渍（随 evilness 增加）
    oil_count = int(e / 20)
    for i in range(oil_count):
        x = 120 + i * 80
        pygame.draw.ellipse(surf, (220, 200, 80), (x, 170, 40, 18))

    # 学生队列（简化）
    base_x, base_y = 120, 260
    for i in range(6):
        x = base_x + i * 80
        # 表情根据 hygiene 改变
        h = state["hygiene"]
        if h > 70:
            color = (80, 180, 80)
        elif h > 40:
            color = (220, 180, 60)
        else:
            color = (200, 90, 90)
        pygame.draw.circle(surf, color, (x, base_y), 24)
        draw_text(surf, f"#{i+1}", (x - 12, base_y - 8), FONT, BLACK)

# ---------- UI 绘制 ----------
def draw_ui(surf):
    # 左上信息
    info_x, info_y = 20, 20
    draw_text(surf, f"Day: {state['day']} / {MAX_DAYS}", (info_x, info_y))
    draw_text(surf, f"Money: ${state['money']}", (info_x, info_y + 22))
    draw_text(surf, f"Evilness: {state['evilness']}", (info_x, info_y + 44))
    draw_text(surf, f"Hygiene: {state['hygiene']}", (info_x, info_y + 66))

    # 右侧按钮
    for b in buttons:
        b.draw(surf)

    # 底部 reviews 展示
    pygame.draw.rect(surf, (240, 240, 240), (20, 520, 680, 100))
    draw_text(surf, "Recent reviews / incidents:", (30, 525), BIGFONT)
    y = 555
    for rev in state["reviews"][-3:]:
        draw_text(surf, "- " + rev["text"], (40, y))
        y += 18

    # messages（top）
    mx, my = 720, 20
    for i, m in enumerate(state["messages"][-3:]):
        rect = pygame.Rect(mx, my + i * 40, 220, 34)
        pygame.draw.rect(surf, (255, 255, 220), rect)
        draw_text(surf, m["text"], (mx + 6, my + i * 40 + 8), FONT)

    # 输入框（typing）
    if state["typing"]:
        ib = pygame.Rect(120, 200, 520, 32)
        pygame.draw.rect(surf, WHITE, ib)
        pygame.draw.rect(surf, BLACK, ib, 2)
        draw_text(surf, "Enter PR slogan: " + state["slogan"], (130, 205), FONT)


# ---------- 消息与 TTL 更新 ----------
def update_messages():
    for m in state["messages"]:
        m["ttl"] -= 1
    state["messages"] = [m for m in state["messages"] if m["ttl"] > 0]

# ---------- 主循环 ----------
def main_loop():
    while True:
        CLOCK.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEMOTION:
                for b in buttons:
                    b.hover = b.rect.collidepoint(event.pos)

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # 点击按钮
                if not state["ended"] and not state["typing"]:
                    for i, b in enumerate(buttons):
                        if b.is_clicked(event.pos):
                            handle_action(i)
                # 若游戏结束，点击任意处重启为 demo（便于展示）
                if state["ended"]:
                    restart_game()

            elif event.type == KEYDOWN:
                if state["typing"]:
                    if event.key == K_RETURN:
                        # 完成 slogan 输入
                        push_message("PR launched: " + state["slogan"])
                        # slogan 有概率短期提升 hygiene（洗白）或引发怀疑
                        if len(state["slogan"]) > 6 and "fresh" in state["slogan"].lower():
                            state["hygiene"] = min(100, state["hygiene"] + 8)
                            push_message("PR worked slightly.")
                        else:
                            # 否则可能被识破
                            if random.random() < 0.4:
                                state["evilness"] += 6
                                push_message("PR is shallow and backfires.")
                        state["typing"] = False
                    elif event.key == K_BACKSPACE:
                        state["slogan"] = state["slogan"][:-1]
                    else:
                        # 仅接受可打印字符
                        ch = event.unicode
                        if ch.isprintable() and len(state["slogan"]) < 40:
                            state["slogan"] += ch
                else:
                    # 普通快捷键（示例）
                    if event.key == K_SPACE and not state["ended"]:
                        next_day()

        # UI 更新
        update_messages()

        # 绘制
        draw_canteen(SCREEN)
        draw_ui(SCREEN)

        # 底部操作提示
        draw_text(SCREEN, "Click buttons on right. Press SPACE to end day / NEXT DAY.", (20, 600), FONT)

        # 结算 / 自动胜利判断
        # 若 money 很低，游戏也可能结束（失败）
        if state["money"] <= 0 and not state["ended"]:
            state["ending_text"] = "Bankrupt! You couldn't keep the canteen running."
            state["ended"] = True

        # 显示结束画面
        if state["ended"]:
            show_end_screen(SCREEN)

        pygame.display.flip()

def show_end_screen(surf):
    # 半透明覆盖
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((30, 30, 30))
    surf.blit(overlay, (0, 0))
    # 结局文本
    draw_text(surf, "=== GAME OVER ===", (WIDTH // 2 - 100, HEIGHT // 2 - 80), BIGFONT, WHITE)
    draw_text(surf, state.get("ending_text", ""), (WIDTH // 2 - 240, HEIGHT // 2 - 40), FONT, WHITE)
    draw_text(surf, f"Final Evilness: {state['evilness']}", (WIDTH // 2 - 120, HEIGHT // 2), FONT, WHITE)
    draw_text(surf, "Click anywhere to restart demo.", (WIDTH // 2 - 150, HEIGHT // 2 + 40), FONT, WHITE)


def restart_game():
    # 重置到初始 demo 状态（老师看 demo 时可以演示多结局）
    state["money"] = 500
    state["evilness"] = 0
    state["hygiene"] = 100
    state["day"] = 1
    state["reviews"] = []
    state["messages"] = []
    state["ended"] = False
    state["typing"] = False
    state["slogan"] = ""

if __name__ == "__main__":
    # 程序开始提示
    push_message("Welcome! Click a button or press SPACE to progress the day.")
    main_loop()
