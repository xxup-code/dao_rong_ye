"""Water Sort Puzzle / 水排序谜题

A puzzle game where players sort colored liquids into bottles.
玩家通过倒酒将每种颜色集中到一个瓶子中。
8 bottles, 5 segments, 7 colors, guaranteed solvable via BFS.
"""
import random
from collections import deque
from typing import List, Optional, Tuple, Dict, Any

import pygame

# ==================== Constants / 常量 ====================
BOTTLE_COUNT: int = 8
SEGMENTS: int = 5
COLOR_COUNT: int = 7
COLORS: List[Tuple[int, int, int]] = [
    (235, 75, 75), (245, 150, 40), (235, 210, 40),
    (70, 190, 70), (50, 175, 210), (75, 90, 225), (170, 70, 210),
]
BG_TOP: Tuple[int, int, int] = (245, 242, 235)
BG_BOT: Tuple[int, int, int] = (225, 220, 210)
BOTTLE_GLASS: Tuple[int, int, int, int] = (200, 195, 185, 160)
PANEL_COLOR: Tuple[int, int, int] = (255, 252, 248)
TEXT_DARK: Tuple[int, int, int] = (55, 45, 35)
TEXT_LIGHT: Tuple[int, int, int] = (140, 130, 120)
GOLD: Tuple[int, int, int] = (230, 180, 60)
BTN_NORMAL: Tuple[int, int, int] = (90, 140, 200)
BTN_HOVER: Tuple[int, int, int] = (110, 160, 220)
BTN_TEXT: Tuple[int, int, int] = (255, 255, 255)

SW: int = 820  # screen width / 屏幕宽度
SH: int = 640  # screen height / 屏幕高度
BOTTLE_W: int = 78
BODY_H: int = 240
SEG_H: int = BODY_H // SEGMENTS
NECK_W: int = 28
NECK_H: int = 28
ROW1_Y: int = 75
ROW2_Y: int = 355

# SDL scancodes — hardware-level, immune to IME / 硬件扫描码，不受输入法影响
SC_L: int = 15
SC_R: int = 21
SC_ESCAPE: int = 41

# Bottle type: list of color indices from bottom to top / 瓶子类型：从底到顶的颜色索引列表
Bottle = List[int]

# ==================== I18n / 国际化 ====================
LANG: str = 'zh'
TEXTS: Dict[str, Dict[str, str]] = {
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
}


def t(key: str, *args: Any) -> str:
    """Get localized text / 获取本地化文本"""
    s: str = TEXTS.get(key, {}).get(LANG, key)
    return s.format(*args) if args else s


# ==================== Puzzle Generation / 谜题生成 ====================

def can_solve(bottles: List[Bottle], max_states: int = 50000) -> bool:
    """BFS: check if the puzzle is solvable / 广度优先搜索验证谜题可解性"""
    start: Tuple[Tuple[int, ...], ...] = tuple(tuple(b) for b in bottles)
    if all(len(set(b)) <= 1 for b in bottles):
        return True
    visited: set = {start}
    q: deque = deque([start])
    while q and len(visited) < max_states:
        cur: List[List[int]] = [list(b) for b in q.popleft()]
        for src in range(BOTTLE_COUNT):
            if not cur[src]:
                continue
            sc: int = cur[src][-1]  # top color / 顶层颜色
            sc_n: int = 0
            for i in range(len(cur[src]) - 1, -1, -1):
                if cur[src][i] == sc:
                    sc_n += 1
                else:
                    break
            for dst in range(BOTTLE_COUNT):
                if src == dst:
                    continue
                if len(cur[dst]) >= SEGMENTS:
                    continue
                if cur[dst] and cur[dst][-1] != sc:  # color mismatch / 颜色不匹配
                    continue
                space: int = SEGMENTS - len(cur[dst])
                pn: int = min(sc_n, space)
                nb: List[List[int]] = [list(b) for b in cur]
                nb[dst].extend([sc] * pn)
                del nb[src][-pn:]
                k: Tuple[Tuple[int, ...], ...] = tuple(tuple(b) for b in nb)
                if k not in visited:
                    if all(len(set(b)) <= 1 for b in nb):
                        return True
                    visited.add(k)
                    q.append(k)
    return False


def generate_puzzle() -> List[Bottle]:
    """Generate a guaranteed-solvable puzzle / 生成保证有解的谜题

    7 colors × 4 units = 28 units, spread across 6 bottles (5 full + 1 partial),
    leaving 2 empty bottles for buffer space.
    """
    for _ in range(200):
        bottles: List[Bottle] = [[] for _ in range(BOTTLE_COUNT)]
        colors: List[int] = []
        for c in range(COLOR_COUNT):
            colors.extend([c] * 4)
        random.shuffle(colors)
        filled: List[int] = random.sample(range(BOTTLE_COUNT), 6)
        idx: int = 0
        for i, b in enumerate(filled):
            n: int = SEGMENTS if i < 5 else 3
            bottles[b] = colors[idx:idx + n]
            idx += n
        random.shuffle(bottles)
        if can_solve(bottles, 50000):
            return bottles
    return generate_fallback()


def generate_fallback() -> List[Bottle]:
    """Simple fallback puzzle / 简单回退谜题"""
    bottles: List[Bottle] = [[] for _ in range(BOTTLE_COUNT)]
    perm: List[int] = list(range(COLOR_COUNT))
    random.shuffle(perm)
    for i in range(4):
        bottles[i] = [perm[i]] * 4
    bottles[4] = [perm[4], perm[5], perm[6], perm[4]]
    bottles[5] = [perm[5]] * 4
    bottles[6] = [perm[6]] * 3
    random.shuffle(bottles)
    return bottles


# ==================== Game Logic / 游戏逻辑 ====================

def is_solved(bottles: List[Bottle]) -> bool:
    """Check if all bottles are pure (single color or empty) / 检查是否全部纯色"""
    return all(len(set(b)) <= 1 for b in bottles)


def get_top_info(bottle: Bottle) -> Tuple[Optional[int], int, int]:
    """Return (top_color, same_color_count, empty_space) / 返回(顶层颜色, 同色数, 空位)"""
    if not bottle:
        return None, 0, SEGMENTS
    top: int = bottle[-1]
    count: int = 0
    for i in range(len(bottle) - 1, -1, -1):
        if bottle[i] == top:
            count += 1
        else:
            break
    space: int = SEGMENTS - len(bottle)
    return top, count, space


# ==================== Drawing Helpers / 绘制辅助 ====================

def darken(c: Tuple[int, int, int], amount: int = 30) -> Tuple[int, int, int]:
    """Darken a color / 颜色加深"""
    return tuple(max(0, v - amount) for v in c)


def lighten(c: Tuple[int, int, int], amount: int = 30) -> Tuple[int, int, int]:
    """Lighten a color / 颜色提亮"""
    return tuple(min(255, v + amount) for v in c)


def draw_bg(screen: pygame.Surface) -> None:
    """Draw gradient background / 绘制渐变背景"""
    for y in range(SH):
        t_val: float = y / SH
        r: int = int(BG_TOP[0] * (1 - t_val) + BG_BOT[0] * t_val)
        g: int = int(BG_TOP[1] * (1 - t_val) + BG_BOT[1] * t_val)
        b: int = int(BG_TOP[2] * (1 - t_val) + BG_BOT[2] * t_val)
        pygame.draw.line(screen, (r, g, b), (0, y), (SW, y))


def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str,
                hover: bool, font: pygame.font.Font) -> pygame.Rect:
    """Draw a button with hover effect / 绘制带悬停效果的按钮"""
    color: Tuple[int, int, int] = BTN_HOVER if hover else BTN_NORMAL
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, darken(color, 20), rect, 2, border_radius=10)
    ts: pygame.Surface = font.render(text, True, BTN_TEXT)
    screen.blit(ts, (rect.x + (rect.w - ts.get_width()) // 2,
                     rect.y + (rect.h - ts.get_height()) // 2))
    return rect


def bottle_center(idx: int) -> Tuple[int, int]:
    """Get bottle mouth center coordinates / 获取瓶子瓶口中心坐标"""
    row: int = idx // 4
    col: int = idx % 4
    x: int = 55 + col * 192 + BOTTLE_W // 2
    y: int = (ROW1_Y if row == 0 else ROW2_Y) + NECK_H // 2
    return x, y


def bottle_rect(idx: int) -> pygame.Rect:
    """Get bottle bounding rectangle / 获取瓶子矩形区域"""
    row: int = idx // 4
    col: int = idx % 4
    x: int = 55 + col * 192
    y: int = ROW1_Y if row == 0 else ROW2_Y
    return pygame.Rect(x, y, BOTTLE_W, BODY_H + NECK_H + 2)


def draw_bottle(screen: pygame.Surface, bottle: Bottle, x: int, y: int,
                selected: bool) -> None:
    """Draw a single bottle with colored segments / 绘制带颜色块的单个瓶子"""
    # inner background / 瓶身内部
    inner: pygame.Rect = pygame.Rect(x + 4, y + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    pygame.draw.rect(screen, (195, 190, 180), inner, border_radius=6)

    # scale marks / 刻度线
    for i in range(1, SEGMENTS):
        ly: int = y + NECK_H + 2 + i * SEG_H
        pygame.draw.line(screen, (170, 165, 155), (x + 6, ly), (x + BOTTLE_W - 6, ly), 1)

    # color blocks from bottom to top / 颜色块从底部向上
    body_bottom: int = y + NECK_H + 2 + BODY_H - 2
    clip_rect: pygame.Rect = pygame.Rect(x + 4, y + NECK_H + 4, BOTTLE_W - 8, BODY_H - 4)
    for i, c in enumerate(bottle):
        seg_top: int = body_bottom - (i + 1) * SEG_H
        seg_top = max(seg_top, y + NECK_H + 6)
        seg_rect: pygame.Rect = pygame.Rect(x + 6, seg_top + 2, BOTTLE_W - 12, SEG_H - 3)
        seg_rect = seg_rect.clip(clip_rect)  # clamp inside bottle / 钳制在瓶身内
        pygame.draw.rect(screen, COLORS[c], seg_rect, border_radius=5)
        if seg_rect.height > 6:
            hl: pygame.Rect = pygame.Rect(seg_rect.x + 3, seg_rect.y + 2,
                                          seg_rect.width - 6, max(3, seg_rect.height // 3))
            pygame.draw.rect(screen, lighten(COLORS[c], 35), hl, border_radius=3)
            sd: pygame.Rect = pygame.Rect(seg_rect.x + 3, seg_rect.y + seg_rect.height - 4,
                                          seg_rect.width - 6, 3)
            pygame.draw.rect(screen, darken(COLORS[c], 25), sd, border_radius=2)

    # glass overlay / 玻璃瓶身
    glass: pygame.Surface = pygame.Surface((BOTTLE_W, BODY_H), pygame.SRCALPHA)
    pygame.draw.rect(glass, BOTTLE_GLASS, pygame.Rect(0, 0, BOTTLE_W, BODY_H), border_radius=10)
    pygame.draw.rect(glass, (120, 115, 108, 200), pygame.Rect(0, 0, BOTTLE_W, BODY_H),
                     2, border_radius=10)
    screen.blit(glass, (x, y + NECK_H + 2))

    # bottle neck / 瓶口
    neck_x: int = x + (BOTTLE_W - NECK_W) // 2
    pygame.draw.rect(screen, (180, 175, 165),
                     pygame.Rect(neck_x, y, NECK_W, NECK_H + 6), border_radius=5)
    pygame.draw.rect(screen, (120, 115, 108),
                     pygame.Rect(neck_x, y, NECK_W, NECK_H + 6), 2, border_radius=5)

    # selection highlight / 选中高亮
    if selected:
        hl: pygame.Rect = pygame.Rect(x - 4, y - 4, BOTTLE_W + 8, BODY_H + NECK_H + 10)
        pygame.draw.rect(screen, GOLD, hl, 3, border_radius=14)


# ==================== Pages / 页面 ====================

def start_page(screen: pygame.Surface, font: pygame.font.Font,
               big_font: pygame.font.Font) -> str:
    """Start page: Start / Settings / Exit / 开始页面"""
    global LANG
    while True:
        mx: int
        my: int
        mx, my = pygame.mouse.get_pos()
        draw_bg(screen)

        ts: pygame.Surface = big_font.render(t('title'), True, TEXT_DARK)
        screen.blit(ts, (SW // 2 - ts.get_width() // 2, 130))

        btn_w: int = 220
        btn_h: int = 52
        sx: int = SW // 2 - btn_w // 2
        hover_start: bool = pygame.Rect(sx, 250, btn_w, btn_h).collidepoint(mx, my)
        hover_sett: bool = pygame.Rect(sx, 320, btn_w, btn_h).collidepoint(mx, my)
        hover_exit: bool = pygame.Rect(sx, 390, btn_w, btn_h).collidepoint(mx, my)

        draw_button(screen, pygame.Rect(sx, 250, btn_w, btn_h),
                    t('start'), hover_start, big_font)
        draw_button(screen, pygame.Rect(sx, 320, btn_w, btn_h),
                    t('settings'), hover_sett, big_font)
        draw_button(screen, pygame.Rect(sx, 390, btn_w, btn_h),
                    t('exit'), hover_exit, big_font)

        hint: pygame.Surface = font.render(
            'L: ' + ('切换语言/Switch Lang', 'Switch Language')[LANG == 'en'],
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


def settings_page(screen: pygame.Surface, font: pygame.font.Font,
                  big_font: pygame.font.Font) -> str:
    """Settings page: language toggle / 设置页面：语言切换"""
    global LANG
    while True:
        mx: int
        my: int
        mx, my = pygame.mouse.get_pos()
        draw_bg(screen)

        ts: pygame.Surface = big_font.render(t('settings'), True, TEXT_DARK)
        screen.blit(ts, (SW // 2 - ts.get_width() // 2, 130))

        btn_w: int = 340
        btn_h: int = 52
        sx: int = SW // 2 - btn_w // 2
        lang_text: str = t('lang_setting')
        hover_lang: bool = pygame.Rect(sx, 250, btn_w, btn_h).collidepoint(mx, my)
        draw_button(screen, pygame.Rect(sx, 250, btn_w, btn_h),
                    lang_text, hover_lang, big_font)

        hover_back: bool = pygame.Rect(sx, 390, btn_w, btn_h).collidepoint(mx, my)
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


# ==================== Game UI / 游戏界面 ====================

def draw_ui(screen: pygame.Surface, bottles: List[Bottle], selected_idx: Optional[int],
            level: int, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    """Draw the game interface / 绘制游戏主界面"""
    draw_bg(screen)

    # top panel / 顶部面板
    panel: pygame.Rect = pygame.Rect(0, 0, SW, 52)
    pygame.draw.rect(screen, PANEL_COLOR, panel)
    pygame.draw.line(screen, (210, 205, 195), (0, 52), (SW, 52), 1)
    title_surf: pygame.Surface = font.render(t('title'), True, TEXT_DARK)
    screen.blit(title_surf, (SW // 2 - title_surf.get_width() // 2, 14))
    lvl_text: pygame.Surface = small_font.render(t('level', level), True, TEXT_LIGHT)
    screen.blit(lvl_text, (14, 18))
    lang_hint: pygame.Surface = small_font.render(f'[{LANG.upper()}]', True, TEXT_LIGHT)
    screen.blit(lang_hint, (SW - 55, 18))

    # draw all bottles / 绘制所有瓶子
    for i in range(BOTTLE_COUNT):
        row: int = i // 4
        col: int = i % 4
        x: int = 55 + col * 192
        y: int = ROW1_Y if row == 0 else ROW2_Y
        draw_bottle(screen, bottles[i], x, y, i == selected_idx)

    # bottom hint / 底部提示
    hint: pygame.Surface = small_font.render(t('hint'), True, TEXT_LIGHT)
    screen.blit(hint, (SW // 2 - hint.get_width() // 2, SH - 28))


def draw_win_overlay(screen: pygame.Surface, font: pygame.font.Font,
                     small_font: pygame.font.Font, level: int,
                     mx: int, my: int) -> Tuple[pygame.Rect, bool]:
    """Draw win dialog with 'continue' button / 绘制通关弹窗"""
    overlay: pygame.Surface = pygame.Surface((SW, SH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))

    bw: int = 380
    bh: int = 200
    bx: int = SW // 2 - bw // 2
    by: int = SH // 2 - bh // 2
    pygame.draw.rect(screen, (255, 250, 240), (bx, by, bw, bh), border_radius=16)
    pygame.draw.rect(screen, GOLD, (bx, by, bw, bh), 3, border_radius=16)

    wt: pygame.Surface = font.render(t('win', level), True, TEXT_DARK)
    screen.blit(wt, (SW // 2 - wt.get_width() // 2, SH // 2 - 30))

    # next level button / 下一关按钮
    nw: int = 180
    nh: int = 44
    nx: int = SW // 2 - nw // 2
    ny: int = SH // 2 + 15
    next_btn: pygame.Rect = pygame.Rect(nx, ny, nw, nh)
    hover: bool = next_btn.collidepoint(mx, my)
    btn_color: Tuple[int, int, int] = BTN_HOVER if hover else BTN_NORMAL
    pygame.draw.rect(screen, btn_color, next_btn, border_radius=8)
    nt: pygame.Surface = small_font.render(t('next'), True, BTN_TEXT)
    screen.blit(nt, (nx + (nw - nt.get_width()) // 2, ny + (nh - nt.get_height()) // 2))
    return next_btn, hover


# ==================== Game Loop / 游戏主循环 ====================

def game_loop(screen: pygame.Surface, font: pygame.font.Font,
              small_font: pygame.font.Font) -> str:
    """Main game loop / 游戏主循环"""
    global LANG
    clock: pygame.time.Clock = pygame.time.Clock()
    level: int = 1
    selected_idx: Optional[int] = None
    won: bool = False
    bottles: List[Bottle] = generate_puzzle()
    next_btn: Optional[pygame.Rect] = None

    running: bool = True
    while running:
        mx: int
        my: int
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
                    selected_idx = None
                    won = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if won and next_btn and next_btn.collidepoint(mx, my):
                    level += 1
                    bottles = generate_puzzle()
                    selected_idx = None
                    won = False
                    continue

                if won:
                    continue

                # detect which bottle was clicked / 检测点击了哪个瓶子
                clicked: Optional[int] = None
                for i in range(BOTTLE_COUNT):
                    row: int = i // 4
                    col: int = i % 4
                    x: int = 55 + col * 192
                    y: int = ROW1_Y if row == 0 else ROW2_Y
                    if pygame.Rect(x, y, BOTTLE_W, BODY_H + NECK_H + 2).collidepoint(mx, my):
                        clicked = i
                        break

                if clicked is not None:
                    if selected_idx is None:
                        # select bottle / 选择瓶子
                        if bottles[clicked]:
                            selected_idx = clicked
                    elif selected_idx == clicked:
                        # deselect / 取消选择
                        selected_idx = None
                    else:
                        # attempt pour / 尝试倒酒
                        src: int = selected_idx
                        dst: int = clicked
                        st: Optional[int]
                        sc: int
                        st, sc, _ = get_top_info(bottles[src])
                        dt: Optional[int]
                        de: int
                        dt, _, de = get_top_info(bottles[dst])
                        if st is not None and de > 0 and (dt is None or dt == st):
                            pour: int = min(sc, de)
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


# ==================== Entry Point / 入口 ====================

def main() -> None:
    """Application entry point / 程序入口"""
    global LANG
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption('Water Sort Puzzle')

    font_path: str = 'C:/Windows/Fonts/msyh.ttc'
    font: pygame.font.Font = pygame.font.Font(font_path, 20)
    big_font: pygame.font.Font = pygame.font.Font(font_path, 28)
    small_font: pygame.font.Font = pygame.font.Font(font_path, 17)

    page: str = 'menu'
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
