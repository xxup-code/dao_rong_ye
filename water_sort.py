"""
水排序谜题 Water Sort Puzzle
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pygame
import random
from collections import deque

# ==================== 常量 ====================
BOTTLE_COUNT = 8
SEGMENTS = 5
COLOR_COUNT = 7
COLORS = [
    (235, 75, 75), (245, 150, 40), (235, 210, 40),
    (70, 190, 70), (50, 175, 210), (75, 90, 225), (170, 70, 210),
]
BG_TOP = (245, 242, 235)
BG_BOT = (225, 220, 210)
BOTTLE_GLASS = (200, 195, 185, 160)
PANEL_COLOR = (255, 252, 248)
TEXT_DARK = (55, 45, 35)
TEXT_LIGHT = (140, 130, 120)
GOLD = (230, 180, 60)
BTN_NORMAL = (90, 140, 200)
BTN_HOVER = (110, 160, 220)
BTN_TEXT = (255, 255, 255)

SW, SH = 820, 640
BOTTLE_W, BODY_H = 78, 240
SEG_H = BODY_H // SEGMENTS
NECK_W, NECK_H = 28, 28
ROW1_Y, ROW2_Y = 75, 355

# SDL scancodes (硬件级，不受IME影响)
SC_L = 15
SC_R = 21
SC_ESCAPE = 41

# ==================== 国际化 ====================
LANG = 'zh'
TEXTS = {
    'title': {'zh': '水排序谜题', 'en': 'Water Sort Puzzle'},
    'level': {'zh': '第 {} 关', 'en': 'Level {}'},
    'win': {'zh': '通过！第 {} 关', 'en': 'Clear! Level {}'},
    'next': {'zh': '按此处继续', 'en': 'Continue'},
    'hint': {'zh': '点击选瓶 → 点目标瓶倒酒 | R重开 | L语言 | ESC退出',
             'en': 'Click select → target pour | R retry | L lang | ESC quit'},
    'start': {'zh': '开始游戏', 'en': 'Start Game'},
    'settings': {'zh': '设置', 'en': 'Settings'},
    'exit': {'zh': '退出', 'en': 'Exit'},
    'lang_setting': {'zh': '语言 / Language: 中文', 'en': 'Language: English'},
    'back': {'zh': '返回', 'en': 'Back'},
    'game_over': {'zh': '通关！', 'en': 'You Win!'},
}
def t(key, *args):
    s = TEXTS.get(key, {}).get(LANG, key)
    return s.format(*args) if args else s


# ==================== 谜题生成 ====================

def can_solve(bottles, max_states=50000):
    start = tuple(tuple(b) for b in bottles)
    if all(len(set(b)) <= 1 for b in bottles):
        return True
    visited = {start}
    q = deque([start])
    while q and len(visited) < max_states:
        cur = [list(b) for b in q.popleft()]
        for src in range(BOTTLE_COUNT):
            if not cur[src]: continue
            sc = cur[src][-1]; sc_n = 0
            for i in range(len(cur[src]) - 1, -1, -1):
                if cur[src][i] == sc: sc_n += 1
                else: break
            for dst in range(BOTTLE_COUNT):
                if src == dst: continue
                if len(cur[dst]) >= SEGMENTS: continue
                if cur[dst] and cur[dst][-1] != sc: continue
                space = SEGMENTS - len(cur[dst])
                pn = min(sc_n, space)
                nb = [list(b) for b in cur]
                nb[dst].extend([sc] * pn)
                del nb[src][-pn:]
                k = tuple(tuple(b) for b in nb)
                if k not in visited:
                    if all(len(set(b)) <= 1 for b in nb):
                        return True
                    visited.add(k)
                    q.append(k)
    return False


def generate_puzzle():
    for _ in range(200):
        bottles = [[] for _ in range(BOTTLE_COUNT)]
        colors = []
        for c in range(COLOR_COUNT):
            colors.extend([c] * 4)
        random.shuffle(colors)
        filled = random.sample(range(BOTTLE_COUNT), 6)
        idx = 0
        for i, b in enumerate(filled):
            n = SEGMENTS if i < 5 else 3
            bottles[b] = colors[idx:idx + n]
            idx += n
        random.shuffle(bottles)
        if can_solve(bottles, 50000):
            return bottles
    return generate_fallback()


def generate_fallback():
    bottles = [[] for _ in range(BOTTLE_COUNT)]
    perm = list(range(COLOR_COUNT)); random.shuffle(perm)
    for i in range(4): bottles[i] = [perm[i]] * 4
    bottles[4] = [perm[4], perm[5], perm[6], perm[4]]
    bottles[5] = [perm[5]] * 4
    bottles[6] = [perm[6]] * 3
    random.shuffle(bottles)
    return bottles


# ==================== 游戏逻辑 ====================

def is_solved(bottles):
    return all(len(set(b)) <= 1 for b in bottles)


def get_top_info(bottle):
    if not bottle:
        return None, 0, SEGMENTS
    top = bottle[-1]
    count = 0
    for i in range(len(bottle) - 1, -1, -1):
        if bottle[i] == top: count += 1
        else: break
    space = SEGMENTS - len(bottle)
    return top, count, space


# ==================== 绘制辅助 ====================

def darken(c, amount=30):
    return tuple(max(0, v - amount) for v in c)

def lighten(c, amount=30):
    return tuple(min(255, v + amount) for v in c)

def draw_bg(screen):
    for y in range(SH):
        t_ = y / SH
        r = int(BG_TOP[0] * (1 - t_) + BG_BOT[0] * t_)
        g = int(BG_TOP[1] * (1 - t_) + BG_BOT[1] * t_)
        b = int(BG_TOP[2] * (1 - t_) + BG_BOT[2] * t_)
        pygame.draw.line(screen, (r, g, b), (0, y), (SW, y))


def draw_button(screen, rect, text, hover, font):
    color = BTN_HOVER if hover else BTN_NORMAL
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, darken(color, 20), rect, 2, border_radius=10)
    ts = font.render(text, True, BTN_TEXT)
    screen.blit(ts, (rect.x + (rect.w - ts.get_width()) // 2,
                     rect.y + (rect.h - ts.get_height()) // 2))
    return rect


def draw_bottle(screen, bottle, x, y, selected):
    inner = pygame.Rect(x + 4, y + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    pygame.draw.rect(screen, (195, 190, 180), inner, border_radius=6)

    for i in range(1, SEGMENTS):
        ly = y + NECK_H + 2 + i * SEG_H
        pygame.draw.line(screen, (170, 165, 155), (x + 6, ly), (x + BOTTLE_W - 6, ly), 1)

    body_bottom = y + NECK_H + 2 + BODY_H - 2
    clip_rect = pygame.Rect(x + 4, y + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    for i, c in enumerate(bottle):
        seg_top = body_bottom - (i + 1) * SEG_H
        seg_top = max(seg_top, y + NECK_H + 6)
        seg_rect = pygame.Rect(x + 6, seg_top + 2, BOTTLE_W - 12, SEG_H - 3)
        seg_rect = seg_rect.clip(clip_rect)
        pygame.draw.rect(screen, COLORS[c], seg_rect, border_radius=5)
        if seg_rect.height > 6:
            hl = pygame.Rect(seg_rect.x + 3, seg_rect.y + 2,
                             seg_rect.width - 6, max(3, seg_rect.height // 3))
            pygame.draw.rect(screen, lighten(COLORS[c], 35), hl, border_radius=3)
            sd = pygame.Rect(seg_rect.x + 3, seg_rect.y + seg_rect.height - 4,
                             seg_rect.width - 6, 3)
            pygame.draw.rect(screen, darken(COLORS[c], 25), sd, border_radius=2)

    glass = pygame.Surface((BOTTLE_W, BODY_H), pygame.SRCALPHA)
    pygame.draw.rect(glass, (200, 195, 188, 70),
                     pygame.Rect(0, 0, BOTTLE_W, BODY_H), border_radius=10)
    pygame.draw.rect(glass, (120, 115, 108, 200),
                     pygame.Rect(0, 0, BOTTLE_W, BODY_H), 2, border_radius=10)
    screen.blit(glass, (x, y + NECK_H + 2))

    neck_x = x + (BOTTLE_W - NECK_W) // 2
    pygame.draw.rect(screen, (180, 175, 165),
                     pygame.Rect(neck_x, y, NECK_W, NECK_H + 6), border_radius=5)
    pygame.draw.rect(screen, (120, 115, 108),
                     pygame.Rect(neck_x, y, NECK_W, NECK_H + 6), 2, border_radius=5)

    if selected:
        hl = pygame.Rect(x - 4, y - 4, BOTTLE_W + 8, BODY_H + NECK_H + 10)
        pygame.draw.rect(screen, GOLD, hl, 3, border_radius=14)


# ==================== 页面 ====================

def start_page(screen, font, big_font):
    """开始页面：开始游戏 / 设置 / 退出"""
    global LANG
    btns = {}
    while True:
        mx, my = pygame.mouse.get_pos()
        draw_bg(screen)

        # 标题
        ts = big_font.render(t('title'), True, TEXT_DARK)
        screen.blit(ts, (SW // 2 - ts.get_width() // 2, 130))

        btn_w, btn_h = 220, 52
        sx = SW // 2 - btn_w // 2
        hover_start = pygame.Rect(sx, 250, btn_w, btn_h).collidepoint(mx, my)
        hover_sett = pygame.Rect(sx, 320, btn_w, btn_h).collidepoint(mx, my)
        hover_exit = pygame.Rect(sx, 390, btn_w, btn_h).collidepoint(mx, my)

        btns['start'] = draw_button(screen, pygame.Rect(sx, 250, btn_w, btn_h),
                                     t('start'), hover_start, big_font)
        btns['settings'] = draw_button(screen, pygame.Rect(sx, 320, btn_w, btn_h),
                                        t('settings'), hover_sett, big_font)
        btns['exit'] = draw_button(screen, pygame.Rect(sx, 390, btn_w, btn_h),
                                    t('exit'), hover_exit, big_font)

        # 操作提示
        hint = font.render('L: ' + ('切换语言/Switch Lang', 'Switch Language')[LANG == 'en'],
                           True, TEXT_LIGHT)
        screen.blit(hint, (SW // 2 - hint.get_width() // 2, 530))

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            if ev.type == pygame.KEYDOWN:
                if ev.scancode == SC_ESCAPE:
                    return 'quit'
                if ev.scancode == SC_L:
                    LANG = 'en' if LANG == 'zh' else 'zh'
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if hover_start:
                    return 'play'
                if hover_sett:
                    return 'settings'
                if hover_exit:
                    return 'quit'


def settings_page(screen, font, big_font):
    """设置页面：语言切换"""
    global LANG
    while True:
        mx, my = pygame.mouse.get_pos()
        draw_bg(screen)

        ts = big_font.render(t('settings'), True, TEXT_DARK)
        screen.blit(ts, (SW // 2 - ts.get_width() // 2, 130))

        # 语言设置按钮
        btn_w, btn_h = 340, 52
        sx = SW // 2 - btn_w // 2
        lang_text = t('lang_setting')
        hover_lang = pygame.Rect(sx, 250, btn_w, btn_h).collidepoint(mx, my)
        draw_button(screen, pygame.Rect(sx, 250, btn_w, btn_h),
                    lang_text, hover_lang, big_font)

        hover_back = pygame.Rect(sx, 390, btn_w, btn_h).collidepoint(mx, my)
        draw_button(screen, pygame.Rect(sx, 390, btn_w, btn_h),
                    t('back'), hover_back, big_font)

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return 'quit'
            if ev.type == pygame.KEYDOWN:
                if ev.scancode == SC_ESCAPE:
                    return 'menu'
                if ev.scancode == SC_L:
                    LANG = 'en' if LANG == 'zh' else 'zh'
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if hover_lang:
                    LANG = 'en' if LANG == 'zh' else 'zh'
                if hover_back:
                    return 'menu'


# ==================== 游戏主循环 ====================

def draw_ui(screen, bottles, selected_idx, level, font, small_font):
    draw_bg(screen)
    # 顶部面板
    panel = pygame.Rect(0, 0, SW, 52)
    pygame.draw.rect(screen, PANEL_COLOR, panel)
    pygame.draw.line(screen, (210, 205, 195), (0, 52), (SW, 52), 1)
    title = font.render(t('title'), True, TEXT_DARK)
    screen.blit(title, (SW // 2 - title.get_width() // 2, 14))
    lvl_text = small_font.render(t('level', level), True, TEXT_LIGHT)
    screen.blit(lvl_text, (14, 18))
    lang_hint = small_font.render(f'[{LANG.upper()}]', True, TEXT_LIGHT)
    screen.blit(lang_hint, (SW - 55, 18))

    for i in range(BOTTLE_COUNT):
        row, col = i // 4, i % 4
        x, y = 55 + col * 192, ROW1_Y if row == 0 else ROW2_Y
        draw_bottle(screen, bottles[i], x, y, i == selected_idx)

    hint = small_font.render(t('hint'), True, TEXT_LIGHT)
    screen.blit(hint, (SW // 2 - hint.get_width() // 2, SH - 28))


def bottle_center(idx):
    """返回瓶子瓶口中心坐标"""
    row, col = idx // 4, idx % 4
    x = 55 + col * 192 + BOTTLE_W // 2
    y = (ROW1_Y if row == 0 else ROW2_Y) + NECK_H // 2
    return x, y


def draw_bottle_surface(bottle, selected=False):
    """将瓶子渲染到独立 Surface"""
    w, h = BOTTLE_W + 12, BODY_H + NECK_H + 12
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    ox, oy = 6, 6

    inner = pygame.Rect(ox + 4, oy + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    pygame.draw.rect(surf, (195, 190, 180), inner, border_radius=6)

    for i in range(1, SEGMENTS):
        ly = oy + NECK_H + 2 + i * SEG_H
        pygame.draw.line(surf, (170, 165, 155), (ox + 6, ly), (ox + BOTTLE_W - 6, ly), 1)

    body_bottom = oy + NECK_H + 2 + BODY_H - 2
    clip_rect = pygame.Rect(ox + 4, oy + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    for i, c in enumerate(bottle):
        seg_top = body_bottom - (i + 1) * SEG_H
        seg_top = max(seg_top, oy + NECK_H + 6)
        seg_rect = pygame.Rect(ox + 6, seg_top + 2, BOTTLE_W - 12, SEG_H - 3)
        seg_rect = seg_rect.clip(clip_rect)
        pygame.draw.rect(surf, COLORS[c], seg_rect, border_radius=5)
        if seg_rect.height > 6:
            hl = pygame.Rect(seg_rect.x + 3, seg_rect.y + 2,
                             seg_rect.width - 6, max(3, seg_rect.height // 3))
            pygame.draw.rect(surf, lighten(COLORS[c], 35), hl, border_radius=3)
            sd = pygame.Rect(seg_rect.x + 3, seg_rect.y + seg_rect.height - 4,
                             seg_rect.width - 6, 3)
            pygame.draw.rect(surf, darken(COLORS[c], 25), sd, border_radius=2)

    gx, gy = ox, oy + NECK_H + 2
    glass = pygame.Surface((BOTTLE_W, BODY_H), pygame.SRCALPHA)
    pygame.draw.rect(glass, (200, 195, 188, 70), (0, 0, BOTTLE_W, BODY_H), border_radius=10)
    pygame.draw.rect(glass, (120, 115, 108, 200), (0, 0, BOTTLE_W, BODY_H), 2, border_radius=10)
    surf.blit(glass, (gx, gy))

    neck_x = ox + (BOTTLE_W - NECK_W) // 2
    pygame.draw.rect(surf, (180, 175, 165),
                     (neck_x, oy, NECK_W, NECK_H + 6), border_radius=5)
    pygame.draw.rect(surf, (120, 115, 108),
                     (neck_x, oy, NECK_W, NECK_H + 6), 2, border_radius=5)

    if selected:
        hl = pygame.Rect(ox - 1, oy - 1, BOTTLE_W + 6, BODY_H + NECK_H + 6)
        pygame.draw.rect(surf, GOLD, hl, 3, border_radius=14)

    return surf


def bottle_rect(idx):
    """返回瓶子的屏幕矩形"""
    row, col = idx // 4, idx % 4
    x = 55 + col * 192
    y = ROW1_Y if row == 0 else ROW2_Y
    return pygame.Rect(x, y, BOTTLE_W, BODY_H + NECK_H + 2)


def draw_pour_anim(screen, anim):
    """倾倒动画：瓶子倾斜，瓶口对瓶口倒液"""
    t = anim['frame'] / anim['max_frames']
    src, dst = anim['src'], anim['dst']
    color = COLORS[anim['color']]
    n = anim['count']

    srect = bottle_rect(src)
    drect = bottle_rect(dst)
    sx0 = srect.x + BOTTLE_W // 2
    sy0 = srect.y + NECK_H // 2
    dx = drect.x + BOTTLE_W // 2
    dy = drect.y + NECK_H // 2

    side = 1 if dx < SW // 2 else -1
    tilt_angle = 55
    hover_x = dx + side * 80
    hover_y = dy - 50

    if t < 0.25:
        lift = t / 0.25
        sx, sy = sx0, sy0 - lift * 50
        tilt = 0; pour_progress = 0.0
    elif t < 0.50:
        move = (t - 0.25) / 0.25
        ease = move * move * (3 - 2 * move)
        sx = sx0 + (hover_x - sx0) * ease
        sy = (sy0 - 50) + (hover_y - (sy0 - 50)) * ease
        tilt = tilt_angle * ease * (-1 if side > 0 else 1)
        pour_progress = 0.0
    elif t < 0.85:
        pour = (t - 0.50) / 0.35
        ease = pour * pour * (3 - 2 * pour)
        sx, sy = hover_x, hover_y
        tilt = tilt_angle * (-1 if side > 0 else 1)
        pour_progress = ease
    else:
        back = (t - 0.85) / 0.15
        ease = back * back * (3 - 2 * back)
        sx = hover_x + (sx0 - hover_x) * ease
        sy = hover_y + (sy0 - hover_y) * ease
        tilt = tilt_angle * (-1 if side > 0 else 1) * (1 - ease)
        pour_progress = 1.0

    transferred = int(n * pour_progress)
    transferred = min(transferred, n)
    if transferred > 0:
        src_vis = anim['src_before'][:-transferred]
    else:
        src_vis = list(anim['src_before'])
    dst_vis = anim['dst_before'] + [anim['color']] * transferred

    draw_bottle(screen, dst_vis, drect.x, drect.y, False)

    surf = draw_bottle_surface(src_vis, False)
    if abs(tilt) > 1:
        surf = pygame.transform.rotate(surf, tilt)
    r = surf.get_rect()
    screen.blit(surf, (sx - r.width // 2, sy - (6 + NECK_H // 2)))

    if pour_progress > 0.02:
        flow = min(1.0, pour_progress * 3)
        n_pts = 30
        for i in range(n_pts):
            p = i / (n_pts - 1)
            bx = sx + (dx - sx) * p + random.uniform(-3, 3) * (1 - p * 0.5)
            by = sy + (dy - sy) * p + 4 * p * (1 - p) * 20
            w = max(1.5, (4 - p * 2) * flow)
            pygame.draw.circle(screen, lighten(color, random.randint(0, 30)),
                               (int(bx), int(by)), int(w))
        for _ in range(int(5 * flow)):
            rx = sx + random.uniform(-4, 4)
            ry = sy + random.uniform(2, 12) * flow
            pygame.draw.circle(screen, lighten(color, 30),
                               (int(rx), int(ry)), int(random.uniform(1, 3)))
        for _ in range(int(3 * flow)):
            rx = dx + random.uniform(-3, 3)
            ry = dy + random.uniform(2, 8) * flow
            pygame.draw.circle(screen, lighten(color, 50),
                               (int(rx), int(ry)), int(random.uniform(1, 3)))



def draw_win_overlay(screen, font, small_font, level, mx, my):
    overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))
    bw, bh = 380, 200
    bx = SW // 2 - bw // 2; by = SH // 2 - bh // 2
    pygame.draw.rect(screen, (255, 250, 240), (bx, by, bw, bh), border_radius=16)
    pygame.draw.rect(screen, GOLD, (bx, by, bw, bh), 3, border_radius=16)
    wt = font.render(t('win', level), True, TEXT_DARK)
    screen.blit(wt, (SW // 2 - wt.get_width() // 2, SH // 2 - 30))

    # 下一关按钮
    nw, nh = 180, 44
    nx = SW // 2 - nw // 2
    ny = SH // 2 + 15
    next_btn = pygame.Rect(nx, ny, nw, nh)
    hover = next_btn.collidepoint(mx, my)
    color = BTN_HOVER if hover else BTN_NORMAL
    pygame.draw.rect(screen, color, next_btn, border_radius=8)
    nt = small_font.render(t('next'), True, BTN_TEXT)
    screen.blit(nt, (nx + (nw - nt.get_width()) // 2, ny + (nh - nt.get_height()) // 2))
    return next_btn, hover


def game_loop(screen, font, small_font):
    """游戏主循环"""
    global LANG
    clock = pygame.time.Clock()
    level = 1; selected_idx = None; won = False
    bottles = generate_puzzle()

    next_btn = None
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

            if event.type == pygame.KEYDOWN:
                if event.scancode == SC_ESCAPE:
                    return 'menu'
                elif event.scancode == SC_L:
                    LANG = 'en' if LANG == 'zh' else 'zh'
                elif event.scancode == SC_R:
                    bottles = generate_puzzle()
                    selected_idx = None; won = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if won and next_btn and next_btn.collidepoint(mx, my):
                    level += 1
                    bottles = generate_puzzle()
                    selected_idx = None; won = False
                    continue

                if won:
                    continue
                mx, my = event.pos
                clicked = None
                for i in range(BOTTLE_COUNT):
                    row, col = i // 4, i % 4
                    x, y = 55 + col * 192, ROW1_Y if row == 0 else ROW2_Y
                    if pygame.Rect(x, y, BOTTLE_W, BODY_H + NECK_H + 2).collidepoint(mx, my):
                        clicked = i; break

                if clicked is not None:
                    if selected_idx is None:
                        if bottles[clicked]:
                            selected_idx = clicked
                    elif selected_idx == clicked:
                        selected_idx = None
                    else:
                        src, dst = selected_idx, clicked
                        st, sc, _ = get_top_info(bottles[src])
                        dt, _, de = get_top_info(bottles[dst])
                        if st is not None and de > 0 and (dt is None or dt == st):
                            pour = min(sc, de)
                            del bottles[src][-pour:]
                            bottles[dst].extend([st] * pour)
                            if is_solved(bottles):
                                won = True
                        selected_idx = None

        draw_ui(screen, bottles, selected_idx, level, font, small_font)

        if won:
            next_btn, _ = draw_win_overlay(screen, font, small_font, level, mx, my)
        pygame.display.flip()
        clock.tick(60)
    return 'quit'


# ==================== 入口 ====================

def main():
    global LANG
    pygame.init()
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption('Water Sort Puzzle')

    font_path = 'C:/Windows/Fonts/msyh.ttc'
    font = pygame.font.Font(font_path, 20)
    big_font = pygame.font.Font(font_path, 28)
    small_font = pygame.font.Font(font_path, 17)

    page = 'menu'
    while page != 'quit':
        if page == 'menu':
            page = start_page(screen, font, big_font)
        elif page == 'settings':
            page = settings_page(screen, font, big_font)
        elif page == 'play':
            page = game_loop(screen, font, small_font)

    pygame.quit()


if __name__ == '__main__':
    main()
