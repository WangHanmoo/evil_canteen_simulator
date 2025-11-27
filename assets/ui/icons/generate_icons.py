"""
生成游戏所需的选项图标和事件配图
"""
import pygame
import os

pygame.init()

def create_icon(filename, size, draw_func):
    """创建一个图标"""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    draw_func(surf, size)
    pygame.image.save(surf, filename)
    print(f"Created: {filename}")

def draw_cockroach(surf, size):
    """蟑螂图标 - 忽略蟑螂"""
    w, h = size
    surf.fill((60, 40, 30))
    # 蟑螂身体
    pygame.draw.ellipse(surf, (40, 25, 15), (w//4, h//4, w//2, h//2))
    # 触角
    pygame.draw.line(surf, (30, 20, 10), (w//2-10, h//4), (w//4, h//8), 2)
    pygame.draw.line(surf, (30, 20, 10), (w//2+10, h//4), (w*3//4, h//8), 2)
    # 红色X表示忽略
    pygame.draw.line(surf, (200, 50, 50), (10, 10), (w-10, h-10), 3)
    pygame.draw.line(surf, (200, 50, 50), (w-10, 10), (10, h-10), 3)

def draw_dirty_plate(surf, size):
    """脏盘子图标"""
    w, h = size
    surf.fill((80, 70, 60))
    # 盘子
    pygame.draw.ellipse(surf, (200, 200, 180), (w//6, h//4, w*2//3, h//2))
    pygame.draw.ellipse(surf, (180, 180, 160), (w//4, h//3, w//2, h//3))
    # 污渍
    pygame.draw.circle(surf, (100, 80, 50), (w//3, h//2), 8)
    pygame.draw.circle(surf, (90, 70, 40), (w*2//3, h//2-5), 6)

def draw_small_portion(surf, size):
    """小份量图标"""
    w, h = size
    surf.fill((70, 60, 50))
    # 碗
    pygame.draw.arc(surf, (220, 200, 180), (w//4, h//3, w//2, h//2), 3.14, 6.28, 3)
    # 很少的食物
    pygame.draw.circle(surf, (180, 120, 80), (w//2, h//2), 10)

def draw_wrong_dish(surf, size):
    """上错菜图标"""
    w, h = size
    surf.fill((60, 60, 70))
    # 问号
    font = pygame.font.SysFont("arial", 48)
    txt = font.render("?", True, (220, 180, 60))
    surf.blit(txt, txt.get_rect(center=(w//2, h//2)))

def draw_quality_food(surf, size):
    """质量食物图标 - 绿色健康"""
    w, h = size
    surf.fill((50, 80, 50))
    # 星星
    points = []
    import math
    cx, cy = w//2, h//2
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        points.append((cx + 20*math.cos(angle), cy + 20*math.sin(angle)))
        angle = math.radians(i * 72 - 90 + 36)
        points.append((cx + 10*math.cos(angle), cy + 10*math.sin(angle)))
    pygame.draw.polygon(surf, (100, 200, 100), points)

def draw_expired(surf, size):
    """过期食材图标"""
    w, h = size
    surf.fill((70, 50, 50))
    # 骷髅符号
    pygame.draw.circle(surf, (200, 200, 180), (w//2, h//3), 15)
    pygame.draw.circle(surf, (50, 30, 30), (w//2-5, h//3-3), 4)
    pygame.draw.circle(surf, (50, 30, 30), (w//2+5, h//3-3), 4)
    # 日期
    font = pygame.font.SysFont("arial", 14)
    txt = font.render("EXP", True, (200, 50, 50))
    surf.blit(txt, txt.get_rect(center=(w//2, h*2//3)))

def draw_insect(surf, size):
    """虫子图标"""
    w, h = size
    surf.fill((60, 50, 40))
    # 多个小虫子
    for pos in [(w//3, h//3), (w*2//3, h//2), (w//2, h*2//3)]:
        pygame.draw.ellipse(surf, (30, 20, 10), (pos[0]-5, pos[1]-3, 10, 6))

def draw_dirty_utensils(surf, size):
    """脏餐具图标"""
    w, h = size
    surf.fill((70, 60, 55))
    # 筷子
    pygame.draw.line(surf, (180, 150, 100), (w//3, h//4), (w//3+5, h*3//4), 4)
    pygame.draw.line(surf, (180, 150, 100), (w//3+15, h//4), (w//3+20, h*3//4), 4)
    # 污渍
    pygame.draw.circle(surf, (80, 60, 40), (w//3+10, h//2), 8)

def draw_clean(surf, size):
    """清洁图标 - 绿色"""
    w, h = size
    surf.fill((50, 90, 70))
    # 闪亮符号
    pygame.draw.line(surf, (200, 255, 200), (w//4, h//2), (w*3//4, h//2), 2)
    pygame.draw.line(surf, (200, 255, 200), (w//2, h//4), (w//2, h*3//4), 2)
    pygame.draw.line(surf, (200, 255, 200), (w//3, h//3), (w*2//3, h*2//3), 2)
    pygame.draw.line(surf, (200, 255, 200), (w*2//3, h//3), (w//3, h*2//3), 2)

# 事件配图
def draw_complaint(surf, size):
    """投诉事件"""
    w, h = size
    surf.fill((80, 50, 50))
    # 愤怒的脸
    pygame.draw.circle(surf, (255, 200, 150), (w//2, h//2), 30)
    # 愤怒眉毛
    pygame.draw.line(surf, (50, 30, 30), (w//2-20, h//2-15), (w//2-10, h//2-10), 3)
    pygame.draw.line(surf, (50, 30, 30), (w//2+20, h//2-15), (w//2+10, h//2-10), 3)
    # 嘴巴
    pygame.draw.arc(surf, (50, 30, 30), (w//2-15, h//2+5, 30, 20), 3.14, 6.28, 2)

def draw_inspector(surf, size):
    """检查员事件"""
    w, h = size
    surf.fill((50, 60, 80))
    # 人形
    pygame.draw.circle(surf, (200, 180, 150), (w//2, h//3), 15)
    pygame.draw.rect(surf, (40, 50, 100), (w//2-15, h//2, 30, 30))
    # 检查板
    pygame.draw.rect(surf, (220, 220, 200), (w//2+20, h//3, 20, 25))
    pygame.draw.line(surf, (50, 50, 50), (w//2+25, h//3+5), (w//2+35, h//3+5), 1)
    pygame.draw.line(surf, (50, 50, 50), (w//2+25, h//3+10), (w//2+35, h//3+10), 1)

def draw_warning(surf, size):
    """警告事件"""
    w, h = size
    surf.fill((90, 60, 30))
    # 警告三角形
    import math
    cx, cy = w//2, h//2
    points = [
        (cx, cy - 25),
        (cx - 25, cy + 20),
        (cx + 25, cy + 20)
    ]
    pygame.draw.polygon(surf, (255, 200, 50), points)
    pygame.draw.polygon(surf, (50, 40, 30), points, 3)
    # 感叹号
    font = pygame.font.SysFont("arial", 30, bold=True)
    txt = font.render("!", True, (50, 40, 30))
    surf.blit(txt, txt.get_rect(center=(cx, cy+5)))

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 生成选项图标 (64x64)
icon_size = (64, 64)
create_icon(os.path.join(SCRIPT_DIR, "opt_cockroach.png"), icon_size, draw_cockroach)
create_icon(os.path.join(SCRIPT_DIR, "opt_dirty_plate.png"), icon_size, draw_dirty_plate)
create_icon(os.path.join(SCRIPT_DIR, "opt_small_portion.png"), icon_size, draw_small_portion)
create_icon(os.path.join(SCRIPT_DIR, "opt_wrong_dish.png"), icon_size, draw_wrong_dish)
create_icon(os.path.join(SCRIPT_DIR, "opt_quality.png"), icon_size, draw_quality_food)
create_icon(os.path.join(SCRIPT_DIR, "opt_expired.png"), icon_size, draw_expired)
create_icon(os.path.join(SCRIPT_DIR, "opt_insect.png"), icon_size, draw_insect)
create_icon(os.path.join(SCRIPT_DIR, "opt_dirty_utensils.png"), icon_size, draw_dirty_utensils)
create_icon(os.path.join(SCRIPT_DIR, "opt_clean.png"), icon_size, draw_clean)

# 生成事件配图 (128x96)
event_size = (128, 96)
create_icon(os.path.join(SCRIPT_DIR, "event_complaint.png"), event_size, draw_complaint)
create_icon(os.path.join(SCRIPT_DIR, "event_inspector.png"), event_size, draw_inspector)
create_icon(os.path.join(SCRIPT_DIR, "event_warning.png"), event_size, draw_warning)

print("\nAll icons generated successfully!")
pygame.quit()
