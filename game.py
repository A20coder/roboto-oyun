import pygame
import sys
import copy
import math
import struct
import json
import os
import random
from levels import LEVELS

# ── Kayıt dosyası ─────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Android'de uygulama klasörü salt-okunur olabilir → yazılabilir özel dizine kaydet
_SAVE_DIR = os.environ.get("ANDROID_PRIVATE", _BASE_DIR)
SAVE_FILE = os.path.join(_SAVE_DIR, "save.json")

# ── Sabitler ──────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 700
PANEL_W = 600      # sağ kontrol paneli genişliği (program alanı bununla genişler)
# Program (komut listesi) yerleşimi — fazla komutlar kaydırılarak gösterilir
PROG_COLS  = 5
PROG_Y0    = 282   # ilk chip y (scroll=0)
PROG_ROW_H = 33    # chip yüksekliği (28) + dikey boşluk (5)
DPAD_H     = 190   # grid altında ok tuşları (D-pad) için ayrılan şerit
FPS = 60
CELL = 52          # varsayılan hücre boyutu (büyük grid'lerde küçülür)
ANIM_SPEED = 8     # robot animasyon hızı (piksel/frame)

# Renkler
BG          = (15,  20,  40)
GRID_BG     = (25,  35,  65)
WALL_C      = (45,  55,  90)
FLOOR_C     = (35,  48,  80)
GOAL_C      = (255, 215,   0)
GOAL_FILL   = (227, 152,  38)   # Roboto hedef sembolü — tok amber
GOAL_RING   = (160,  98,  16)   # hedef dış halka (koyu)
ROBOT_C     = (80,  200, 255)
BOX_C       = (200, 120,  50)
PANEL_C     = (26,  31,  46)   # #1a1f2e
BTN_RUN     = (34,  197,  94)  # #22c55e
BTN_CLEAR   = (239,  68,  68)  # #ef4444
BTN_RESET   = (59,  130, 246)  # #3b82f6
BTN_STEP    = (80,  150, 255)
TEXT_C      = (220, 230, 255)
TEXT_DARK   = (139, 154, 191)  # #8b9abf
STAR_ON     = (251, 191,  36)  # #fbbf24
STAR_OFF    = (42,   48,  80)  # #2a3050
CYAN_C      = (126, 207, 255)  # #7ecfff
CMD_COLORS  = {
    "YUKARI":    (59,  130, 246),  # #3b82f6
    "AŞAĞI":     (34,  197,  94),  # #22c55e
    "SOLA":      (168,  85, 247),  # #a855f7
    "SAĞA":      (239,  68,  68),  # #ef4444
    "TEKRAR x2": (245, 158,  11),  # #f59e0b
    "TEKRAR x3": (249, 115,  22),  # #f97316
}
CMD_BOT = {   # gradient koyu alt renk (#1d4ed8 vb.)
    "YUKARI":    (29,   78, 216),
    "AŞAĞI":     (21,  128,  61),
    "SOLA":      (126,  34, 206),
    "SAĞA":      (185,  28,  28),
    "TEKRAR x2": (180,  83,   9),
    "TEKRAR x3": (194,  65,  12),
}
CMD_SHADOW_C = {  # 3D alt gölge (box-shadow 0 4px 0)
    "YUKARI":    (30,  58, 138),
    "AŞAĞI":     (20,  83,  45),
    "SOLA":      (88,  28, 135),
    "SAĞA":      (127,  29,  29),
    "TEKRAR x2": (120,  53,  15),
    "TEKRAR x3": (124,  45,  18),
}
CMD_ICONS = {
    "YUKARI":    "▲",
    "AŞAĞI":     "▼",
    "SOLA":      "←",
    "SAĞA":      "→",
    "TEKRAR x2": "2×",
    "TEKRAR x3": "3×",
}
CONCEPT_C = {
    "Sıralama": (80, 180, 255),
    "Dönüş":    (180, 80, 255),
    "Döngü":    (80, 220, 150),
    "Koşul":    (255, 160, 60),
    "Hepsi":    (255, 215, 0),
}

# ── Tema (koyu / açık) ──────────────────────────────────────────────────────
# Bu renkler menüdeki tema butonuyla değiştirilir. Fonksiyonlar bu globalleri
# çalışma anında okuduğu için apply_theme() yeniden atayınca her yer güncellenir.
DARK_PALETTE = {
    "BG": (15, 20, 40), "GRID_BG": (25, 35, 65), "WALL_C": (45, 55, 90),
    "FLOOR_C": (35, 48, 80), "PANEL_C": (26, 31, 46),
    "TEXT_C": (220, 230, 255), "TEXT_DARK": (139, 154, 191),
    "CYAN_C": (126, 207, 255), "TITLE_C": (255, 215, 0),
    "CARD_BG": (18, 22, 38), "CARD_BD": (40, 55, 90), "CARD_LOCK": (12, 15, 25),
}
LIGHT_PALETTE = {
    "BG": (208, 215, 228), "GRID_BG": (182, 193, 213), "WALL_C": (108, 124, 158),
    "FLOOR_C": (200, 209, 224), "PANEL_C": (214, 221, 233),
    "TEXT_C": (28, 38, 66), "TEXT_DARK": (92, 108, 142),
    "CYAN_C": (36, 104, 162), "TITLE_C": (200, 120, 12),
    "CARD_BG": (222, 229, 240), "CARD_BD": (176, 188, 210), "CARD_LOCK": (192, 201, 216),
}

def apply_theme(dark):
    globals().update(DARK_PALETTE if dark else LIGHT_PALETTE)

apply_theme(True)   # başlangıç: koyu tema

COMMANDS = ["YUKARI", "AŞAĞI", "SOLA", "SAĞA", "TEKRAR x2", "TEKRAR x3"]
CMD_KEYS = {cmd: str(i + 1) for i, cmd in enumerate(COMMANDS)}
DIRS = [(0, -1), (-1, 0), (1, 0), (0, 1)]  # Yukarı Sol Sağ Aşağı (col,row)
DIR_NAMES = ["↑", "←", "→", "↓"]


def expand_commands(cmds):
    """TEKRAR komutlarını aç."""
    result = []
    i = 0
    while i < len(cmds):
        c = cmds[i]
        if c == "TEKRAR x2":
            block = [x for x in cmds[:i] if x not in ("TEKRAR x2", "TEKRAR x3")]
            result.extend(block)
            i += 1
            continue
        if c == "TEKRAR x3":
            block = [x for x in cmds[:i] if x not in ("TEKRAR x2", "TEKRAR x3")]
            result.extend(block)
            result.extend(block)
            i += 1
            continue
        result.append(c)
        i += 1
    return result


def parse_grid(raw):
    grid = []
    start = goal = None
    for r, row in enumerate(raw):
        line = []
        for c, ch in enumerate(row):
            if ch == "S":
                start = (c, r)
                line.append(".")
            elif ch == "G":
                goal = (c, r)
                line.append(".")
            else:
                line.append(ch)
        grid.append(line)
    return grid, start, goal


class Robot:
    def __init__(self, col, row, cell=CELL):
        self.col  = col
        self.row  = row
        self.cell = cell
        self.dir  = 2
        self.px   = col * cell
        self.py   = row * cell
        self.moving    = False
        self.target_px = self.px
        self.target_py = self.py

    def snap(self):
        self.px = self.col * self.cell
        self.py = self.row * self.cell
        self.target_px = self.px
        self.target_py = self.py
        self.moving = False

    def update_anim(self):
        if not self.moving:
            return
        dx = self.target_px - self.px
        dy = self.target_py - self.py
        if abs(dx) < ANIM_SPEED and abs(dy) < ANIM_SPEED:
            self.px = self.target_px
            self.py = self.target_py
            self.moving = False
        else:
            self.px += ANIM_SPEED if dx > 0 else (-ANIM_SPEED if dx < 0 else 0)
            self.py += ANIM_SPEED if dy > 0 else (-ANIM_SPEED if dy < 0 else 0)


def draw_robot(surf, rx, ry, dir_idx, cell):
    cx = rx + cell // 2
    cy = ry + cell // 2
    r = cell // 2 - 4
    pygame.draw.circle(surf, ROBOT_C, (cx, cy), r)
    pygame.draw.circle(surf, BG, (cx, cy), r - 6)
    # göz
    ex, ey = DIRS[dir_idx]
    eye_x = cx + ex * (r // 2)
    eye_y = cy + ey * (r // 2)
    pygame.draw.circle(surf, ROBOT_C, (eye_x, eye_y), 5)


def draw_star(surf, cx, cy, r, filled, color=None):
    if color is None:
        color = STAR_ON if filled else STAR_OFF
    pts = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((round(cx + rr * math.cos(angle)),
                    round(cy - rr * math.sin(angle))))
    pygame.draw.polygon(surf, color, pts)


def _make_blip(freq=820, duration=0.07, volume=0.35):
    rate = 22050
    n    = int(rate * duration)
    buf  = bytearray(n * 2)
    for i in range(n):
        env = (1 - i / n) ** 1.8
        val = int(28000 * volume * math.sin(2 * math.pi * freq * i / rate) * env)
        struct.pack_into("<h", buf, i * 2, max(-32768, min(32767, val)))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _make_success_sound():
    rate = 22050
    notes = [523, 659, 784, 1047]
    n_per = int(rate * 0.09)
    buf = bytearray()
    for freq in notes:
        for i in range(n_per):
            env = (1 - i / n_per) ** 1.2
            val = int(28000 * 0.32 * math.sin(2 * math.pi * freq * i / rate) * env)
            buf.extend(struct.pack("<h", max(-32768, min(32767, val))))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _make_fail_sound():
    rate = 22050
    n = int(rate * 0.28)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / n
        freq = 280 - 130 * t
        env = (1 - t) ** 0.6
        val = int(24000 * 0.38 * math.sin(2 * math.pi * freq * i / rate) * env)
        struct.pack_into("<h", buf, i * 2, max(-32768, min(32767, val)))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _make_menu_music():
    rate   = 22050
    bpm    = 120
    beat_n = int(rate * 60 / bpm)

    # Do majör — parlak, neşeli "yaz" havası (I–V–vi–IV: C–G–Am–F)
    # Bas notaları
    F2, G2, A2, B2 = 87.31, 98.00, 110.00, 123.47
    C3, D3, E3, G3 = 130.81, 146.83, 164.81, 196.00
    # Melodi notaları
    F4, G4, A4, B4 = 349.23, 392.00, 440.00, 493.88
    C5, D5, E5     = 523.25, 587.33, 659.25

    melody = [
        # C                                   # G
        (G4,.5),(C5,.5),(E5,.5),(C5,.5),(G4,.5),(C5,.5),(E5,1.0),
        (D5,.5),(B4,.5),(G4,.5),(B4,.5),(D5,.5),(B4,.5),(D5,1.0),
        # Am                                  # F
        (C5,.5),(A4,.5),(E5,.5),(C5,.5),(A4,.5),(C5,.5),(A4,1.0),
        (A4,.5),(F4,.5),(C5,.5),(A4,.5),(F4,.5),(A4,.5),(C5,1.0),
    ]
    bass = [
        (C3,1),(C3,1),(E3,1),(G3,1),
        (G2,1),(G2,1),(B2,1),(D3,1),
        (A2,1),(A2,1),(C3,1),(E3,1),
        (F2,1),(F2,1),(A2,1),(C3,1),
    ]

    total = sum(int(d * beat_n) for _, d in melody)
    arr   = [0.0] * total

    def mix(seq, vol, decay=1.3, harm=0.0):
        pos = 0
        for freq, beats in seq:
            n_s = int(beats * beat_n)
            for i in range(n_s):
                if pos + i < total:
                    t   = i / n_s
                    # marimba/ukulele benzeri "pluck": hızlı atak + üstel sönüm
                    env = min(t / 0.015, 1.0) * (1.0 - t) ** decay
                    ph  = 2 * math.pi * freq * i / rate
                    arr[pos + i] += vol * env * (math.sin(ph) + harm * math.sin(2 * ph))
            pos += n_s

    mix(melody, 0.50, decay=1.4, harm=0.35)
    mix(bass,   0.34, decay=1.0)

    peak  = max(abs(v) for v in arr) or 1.0
    scale = 26000 / peak
    buf   = bytearray(total * 2)
    for i, v in enumerate(arr):
        struct.pack_into("<h", buf, i * 2, max(-32768, min(32767, int(v * scale))))
    return pygame.mixer.Sound(buffer=bytes(buf))


ANDROID = any(k in os.environ for k in
              ("ANDROID_ARGUMENT", "ANDROID_APP_PATH", "ANDROID_PRIVATE"))


class _SilentSound:
    """Ses aygıtı yoksa (bazı telefonlarda) çökmesin diye sessiz yedek."""
    def play(self, *a, **k):
        return None

    def stop(self, *a, **k):
        pass


class Game:
    def __init__(self):
        # Sesi güvenli başlat — aygıt yoksa oyun yine de çalışsın
        self._snd_on = True
        try:
            pygame.mixer.pre_init(22050, -16, 1, 256)
        except Exception:
            pass
        pygame.init()
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(22050, -16, 1, 256)
        except Exception:
            self._snd_on = False

        # Masaüstünde pencere, Android'de tam ekran. Tüm çizim 1280x700'lük
        # sanal tuvale yapılır, sonra cihaz ekranına ölçeklenerek basılır.
        if ANDROID:
            # Cihazın gerçek çözünürlüğünü al, tam ekran aç
            info = pygame.display.Info()
            self.display = pygame.display.set_mode((info.current_w, info.current_h),
                                                   pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Roboto'yu Kurtar!")
        dw, dh = self.display.get_size()
        self._grad_cache = {}    # gradyan yüzeyleri önbelleği (performans)
        self._scale = min(dw / SCREEN_W, dh / SCREEN_H)
        self._sw, self._sh = int(SCREEN_W * self._scale), int(SCREEN_H * self._scale)
        self._ox = (dw - self._sw) // 2
        self._oy = (dh - self._sh) // 2
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))   # sanal ekran (çizim yüzeyi)

        self.clock = pygame.time.Clock()

        self.font_big   = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_med   = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_sm    = pygame.font.SysFont("segoeui", 16)
        self.font_xs    = pygame.font.SysFont("segoeui", 12, bold=True)
        self.font_prog  = pygame.font.SysFont("segoeui", 14, bold=True)
        _hint_path  = pygame.font.match_font("Georgia") or pygame.font.match_font("Palatino Linotype") or pygame.font.match_font("Garamond")
        self.font_hint  = pygame.font.Font(_hint_path, 16) if _hint_path else pygame.font.SysFont("segoeui", 14)
        _badge_path = pygame.font.match_font("Bahnschrift") or pygame.font.match_font("Candara")
        self.font_badge = pygame.font.Font(_badge_path, 13) if _badge_path else pygame.font.SysFont("segoeui", 11, bold=True)
        self.font_title = pygame.font.SysFont("segoeui", 36, bold=True)
        # Başlık için daha şık font — Bahnschrift (modern geometrik), yoksa Candara
        _title_font = next(
            (f for f in ("Bahnschrift", "Candara", "Trebuchet MS") if pygame.font.match_font(f)),
            "segoeui"
        )
        self.font_title_main = pygame.font.SysFont(_title_font, 52, bold=True)

        def _snd(maker):
            if not self._snd_on:
                return _SilentSound()
            try:
                return maker()
            except Exception:
                return _SilentSound()
        self.add_sound      = _snd(_make_blip)
        self.success_sound  = _snd(_make_success_sound)
        self.fail_sound     = _snd(_make_fail_sound)
        self.menu_music     = _snd(_make_menu_music)
        self.menu_channel   = None
        self.music_paused   = False
        self.font_emoji = pygame.font.SysFont("Segoe UI Emoji", 30)

        self.last_added_idx  = -1
        self.last_added_time = 0

        self.level_idx   = 0
        self.stars_earned = [0] * len(LEVELS)
        self.confetti     = []
        self.scene        = "menu"
        self.timer_enabled = True      # kronometre açık/kapalı (menüden ayarlanır)
        self.timer_start   = 0
        self.solve_time    = None      # bölüm çözülünce dondurulan süre (ms)
        self.dark_theme    = True      # koyu/açık tema (menüden ayarlanır)
        self.load_level(self.level_idx)
        self._load_save()
        apply_theme(self.dark_theme)

    # ── Bölüm yükleme ─────────────────────────────────────────────────────────
    def load_level(self, idx, reset_timer=True):
        lvl = LEVELS[idx]
        self.grid_raw, self.start, self.goal = parse_grid(lvl["grid"])
        self.grid  = copy.deepcopy(self.grid_raw)
        # Önce cell hesapla, sonra robot oluştur
        g_rows = len(self.grid)
        g_cols = max(len(r) for r in self.grid)
        avail_w = (SCREEN_W - PANEL_W) - 20
        avail_h = SCREEN_H - 20 - DPAD_H      # alt şerit D-pad'e ayrıldı
        self.cell = min(CELL,
                        avail_w // max(g_cols, 1),
                        avail_h // max(g_rows, 1))
        self.robot = Robot(*self.start, cell=self.cell)
        self.robot.snap()
        self.commands     = []
        self.running      = False
        self.run_queue    = []
        self.run_index    = 0
        self.waiting_anim = False
        self.success      = False
        self.fail_msg     = ""
        self.step_count   = 0
        self.last_added_idx  = -1
        self.last_added_time = 0
        self.prog_scroll  = 0
        # Kronometre: yalnızca bölüme girince/yeniden başlatınca sıfırlanır.
        # ÇALIŞTIR/TEMİZLE robotu başa alırken (reset_timer=False) süre korunur,
        # böylece Roboto kurtarılana kadar kronometre saymaya devam eder.
        if reset_timer:
            self.timer_start = pygame.time.get_ticks()
        self.solve_time = None

    # ── Kayıt ─────────────────────────────────────────────────────────────────
    def _load_save(self):
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            for i, s in enumerate(data.get("stars", [])):
                if i < len(self.stars_earned):
                    self.stars_earned[i] = s
            self.timer_enabled = bool(data.get("timer", self.timer_enabled))
            self.dark_theme = bool(data.get("dark", self.dark_theme))
        except Exception:
            pass

    def _save_game(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump({"stars": self.stars_earned,
                           "timer": self.timer_enabled,
                           "dark": self.dark_theme}, f)
        except Exception:
            pass

    def _is_unlocked(self, idx):
        return idx == 0 or self.stars_earned[idx - 1] > 0

    def _music_btn_rect(self):
        return pygame.Rect(SCREEN_W - 52, 12, 40, 40)

    def _timer_btn_rect(self):
        return pygame.Rect(SCREEN_W // 2 - 120, 548, 240, 40)

    def _theme_btn_rect(self):
        return pygame.Rect(SCREEN_W - 182, SCREEN_H - 50, 168, 36)

    def _draw_theme_btn(self):
        r   = self._theme_btn_rect()
        lbl = "TEMA: KOYU" if self.dark_theme else "TEMA: AÇIK"
        self._draw_button(lbl, r.x, r.y, r.w, r.h, WALL_C, shadow=False)

    @staticmethod
    def _fmt_time(ms):
        s = max(0, ms) // 1000
        return f"{s // 60}:{s % 60:02d}"

    def _draw_clock_time(self, right_x, cy, ms, color):
        """Sağa hizalı: küçük saat ikonu + süre metni."""
        ts = self.font_sm.render(self._fmt_time(ms), True, color)
        tx = right_x - ts.get_width()
        self.screen.blit(ts, (tx, cy - ts.get_height() // 2))
        r   = 7
        ccx = tx - 9 - r
        pygame.draw.circle(self.screen, color, (ccx, cy), r, 2)
        pygame.draw.line(self.screen, color, (ccx, cy), (ccx, cy - r + 3), 2)
        pygame.draw.line(self.screen, color, (ccx, cy), (ccx + r - 4, cy), 2)

    def _toggle_music(self):
        self.music_paused = not self.music_paused
        if self.music_paused:
            if self.menu_channel and self.menu_channel.get_busy():
                self.menu_channel.pause()
        else:
            if self.menu_channel:
                self.menu_channel.unpause()
            else:
                self.menu_channel = self.menu_music.play(loops=-1, fade_ms=400)

    def _set_fail(self, msg):
        self.fail_msg = msg
        self.running = False
        self.fail_sound.play()

    # ── Konfeti ───────────────────────────────────────────────────────────────
    def _spawn_confetti(self):
        colors = [GOAL_C, ROBOT_C, (255, 100, 150), (100, 255, 150), (180, 100, 255)]
        self.confetti = [
            [
                random.randint(0, SCREEN_W),
                random.uniform(-120, -10),
                random.uniform(-1.8, 1.8),
                random.uniform(2.5, 5.5),
                random.choice(colors),
                random.randint(5, 13),
                255.0,
                random.uniform(0, 360),
                random.uniform(-5, 5),
            ]
            for _ in range(110)
        ]

    def _update_confetti(self):
        survivors = []
        for p in self.confetti:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.12
            p[6] = max(0.0, p[6] - 1.2)
            p[7] += p[8]
            if p[1] < SCREEN_H + 30 and p[6] > 0:
                survivors.append(p)
        self.confetti = survivors

    def _draw_confetti(self):
        for p in self.confetti:
            x, y, _, _, color, size, alpha, angle, _ = p
            s = pygame.Surface((size * 2 + 2, size + 2), pygame.SRCALPHA)
            pygame.draw.rect(s, (*color, int(alpha)), (0, 0, size * 2, size))
            rs = pygame.transform.rotate(s, angle)
            self.screen.blit(rs, (int(x) - rs.get_width() // 2,
                                  int(y) - rs.get_height() // 2))

    # ── Ana döngü ─────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                if self.scene == "game":
                    self.scene = "menu"
                elif self.scene in ("win", "levelsel"):
                    self.scene = "menu"
            if e.type == pygame.KEYDOWN and self.scene == "game" and not self.running:
                num_map = {
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                    pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
                }
                arrow_map = {
                    pygame.K_UP: "YUKARI", pygame.K_DOWN: "AŞAĞI",
                    pygame.K_LEFT: "SOLA", pygame.K_RIGHT: "SAĞA",
                    pygame.K_w: "YUKARI", pygame.K_s: "AŞAĞI",
                    pygame.K_a: "SOLA",   pygame.K_d: "SAĞA",
                }
                if e.key in num_map:
                    self._add_command(COMMANDS[num_map[e.key]])
                elif e.key in arrow_map:
                    self._manual_step(arrow_map[e.key])
                elif e.key == pygame.K_c:
                    if self.commands:
                        self._start_run()
                elif e.key == pygame.K_t:
                    self.commands = []
                    self.fail_msg = ""
                    self.load_level(self.level_idx, reset_timer=False)
                elif e.key in (pygame.K_z, pygame.K_BACKSPACE):
                    self._undo_command()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.handle_click(self.to_canvas(e.pos))
            if e.type == pygame.MOUSEWHEEL and self.scene == "game":
                self.prog_scroll -= e.y * PROG_ROW_H
                self._clamp_prog_scroll()

    def update(self):
        if self.scene == "win":
            self._update_confetti()
        # Menü müziği kontrolü
        if self.scene in ("menu", "levelsel"):
            if not self.music_paused:
                if self.menu_channel is None or not self.menu_channel.get_busy():
                    self.menu_channel = self.menu_music.play(loops=-1, fade_ms=600)
        else:
            if self.menu_channel is not None and self.menu_channel.get_busy():
                self.menu_channel.fadeout(500)
            self.menu_channel = None
        if self.scene != "game":
            return
        # Robot hareket animasyonu — hem program hem de elle (ok) hareketi için
        if self.robot.moving:
            self.robot.update_anim()
            if not self.robot.moving:
                self.waiting_anim = False
                if (self.robot.col, self.robot.row) == self.goal:
                    self._win_level()
                elif self.running:
                    self._next_command()
            return
        # Program çalışıyorsa sıradaki komutu işle
        if self.running and self.run_index < len(self.run_queue):
            self._exec_command(self.run_queue[self.run_index])
            self.run_index += 1

    def _win_level(self):
        self.success = True
        self.running = False
        self.solve_time = pygame.time.get_ticks() - self.timer_start
        earned = self._calc_stars()
        self.stars_earned[self.level_idx] = max(self.stars_earned[self.level_idx], earned)
        self._save_game()
        self._spawn_confetti()
        self.success_sound.play()
        self.scene = "win"

    def _manual_step(self, cmd):
        """Ok tuşu/butonu ile Roboto'yu tek adım hareket ettir (program gerekmez)."""
        if self.running or self.success or self.robot.moving:
            return
        move_map = {"YUKARI": (0, -1), "AŞAĞI": (0, 1), "SOLA": (-1, 0), "SAĞA": (1, 0)}
        dir_idx  = {"YUKARI": 0, "SOLA": 1, "SAĞA": 2, "AŞAĞI": 3}
        dc, dr = move_map[cmd]
        self.robot.dir = dir_idx[cmd]
        nc, nr = self.robot.col + dc, self.robot.row + dr
        if self._walkable(nc, nr):
            self.robot.col, self.robot.row = nc, nr
            self.robot.target_px = nc * self.cell
            self.robot.target_py = nr * self.cell
            self.robot.moving = True
            self.step_count += 1
            self.fail_msg = ""
            self.add_sound.play()

    def _calc_stars(self):
        # Bitirme süresine göre: ≤15sn → 3, 15–30sn → 2, >30sn → 1 yıldız
        secs = (self.solve_time or 0) / 1000
        if secs <= 15:
            return 3
        if secs <= 30:
            return 2
        return 1

    def _finish_run(self):
        """Çalıştırma bittiğinde: komutlar tüketildi, robot bulunduğu yerde kalır."""
        self.running   = False
        self.run_queue = []
        self.run_index = 0
        self.commands  = []
        self.prog_scroll = 0

    def _next_command(self):
        if self.run_index >= len(self.run_queue):
            at_goal = (self.robot.col, self.robot.row) == self.goal
            self._finish_run()
            if not at_goal:
                self.fail_msg = "Henüz hedefte değilsin — oklarla veya komutla devam et."

    def _exec_command(self, cmd):
        move_map = {"YUKARI": (0, -1), "AŞAĞI": (0, 1), "SOLA": (-1, 0), "SAĞA": (1, 0)}
        dir_idx  = {"YUKARI": 0, "SOLA": 1, "SAĞA": 2, "AŞAĞI": 3}
        if cmd in move_map:
            dc, dr = move_map[cmd]
            nc, nr = self.robot.col + dc, self.robot.row + dr
            self.robot.dir = dir_idx[cmd]
            if self._walkable(nc, nr):
                self.robot.col = nc
                self.robot.row = nr
                self.robot.target_px = nc * self.cell
                self.robot.target_py = nr * self.cell
                self.robot.moving = True
                self.step_count += 1
            else:
                self._set_fail("Duvara çarptı! Yolu tekrar planla.")
                self._finish_run()
        self.waiting_anim = True

    def _walkable(self, c, r):
        if r < 0 or r >= len(self.grid): return False
        if c < 0 or c >= len(self.grid[r]): return False
        return self.grid[r][c] in (".", "G", "S")

    # ── Tıklama işlemleri ─────────────────────────────────────────────────────
    def handle_click(self, pos):
        if self.scene == "menu":
            self._click_menu(pos)
        elif self.scene == "game":
            self._click_game(pos)
        elif self.scene == "win":
            self._click_win(pos)
        elif self.scene == "levelsel":
            self._click_levelsel(pos)

    def _click_menu(self, pos):
        if self._music_btn_rect().collidepoint(pos):
            self._toggle_music()
            return
        # Kronometre aç/kapa
        if self._timer_btn_rect().collidepoint(pos):
            self.timer_enabled = not self.timer_enabled
            self._save_game()
            return
        # Tema (koyu/açık) değiştir
        if self._theme_btn_rect().collidepoint(pos):
            self.dark_theme = not self.dark_theme
            apply_theme(self.dark_theme)
            self._save_game()
            return
        # Oyna butonu — ilk tamamlanmamış bölümden başla
        if self._btn_rect(SCREEN_W//2 - 120, 310, 240, 55).collidepoint(pos):
            first_incomplete = next(
                (i for i, s in enumerate(self.stars_earned) if s == 0),
                len(LEVELS) - 1
            )
            self.level_idx = first_incomplete
            self.load_level(self.level_idx)
            self.scene = "game"
        # Bölüm Seç
        if self._btn_rect(SCREEN_W//2 - 120, 410, 240, 55).collidepoint(pos):
            self.scene = "levelsel"

    def _click_win(self, pos):
        # Sonraki Bölüm
        if self.level_idx < len(LEVELS) - 1:
            if self._btn_rect(SCREEN_W//2 - 130, 440, 260, 55).collidepoint(pos):
                self.level_idx += 1
                self.load_level(self.level_idx)
                self.scene = "game"
        # Tekrar
        if self._btn_rect(SCREEN_W//2 - 130, 510, 260, 55).collidepoint(pos):
            self.load_level(self.level_idx)
            self.scene = "game"
        # Menü
        if self._btn_rect(SCREEN_W//2 - 130, 580, 260, 55).collidepoint(pos):
            self.scene = "menu"

    def _click_levelsel(self, pos):
        for i in range(len(LEVELS)):
            if self._levelsel_rect(i).collidepoint(pos):
                if self._is_unlocked(i):
                    self.level_idx = i
                    self.load_level(i)
                    self.scene = "game"
                return
        if self._btn_rect(SCREEN_W//2 - 80, SCREEN_H - 50, 160, 38).collidepoint(pos):
            self.scene = "menu"

    def _click_game(self, pos):
        if self.running:
            return
        panel_x = SCREEN_W - PANEL_W

        # Ok tuşları (D-pad) — Roboto'yu elle hareket ettir
        for cmd, r in self._dpad_rects().items():
            if r.collidepoint(pos):
                self._manual_step(cmd)
                return

        # Komut butonları
        for i, cmd in enumerate(COMMANDS):
            r = self._cmd_btn_rect(i, panel_x)
            if r.collidepoint(pos):
                self._add_command(cmd)
                return

        # Program listesindeki komutları sil (yalnızca görünür alandakiler)
        if self._prog_area_rect(panel_x).collidepoint(pos):
            for i in range(len(self.commands)):
                r = self._prog_item_rect(i, panel_x)
                if r.collidepoint(pos):
                    self.commands.pop(i)
                    self.fail_msg = ""
                    self._clamp_prog_scroll()
                    break
            return

        run_r, clr_r, rst_r = self._action_btn_rects(panel_x)

        # ÇALIŞTIR butonu
        if self._btn_rect(*run_r).collidepoint(pos):
            if self.commands:
                self._start_run()
            return

        # TEMİZLE butonu
        if self._btn_rect(*clr_r).collidepoint(pos):
            self.commands = []
            self.fail_msg = ""
            self.load_level(self.level_idx, reset_timer=False)
            return

        # GERİ AL butonu — son eklenen komutu sil
        if self._btn_rect(*rst_r).collidepoint(pos):
            self._undo_command()
            return

        # Geri (menü)
        if self._menu_back_rect().collidepoint(pos):
            self.scene = "menu"

    def _undo_command(self):
        if self.commands:
            self.commands.pop()
            self.fail_msg = ""
            self.last_added_idx = -1

    def _start_run(self):
        # Robotu BAŞA ALMADAN bulunduğu yerden çalıştır (oklarla gelinen yerden devam)
        if self.robot.moving or self.success:
            return
        self.run_queue = expand_commands(list(self.commands))
        self.run_index = 0
        self.fail_msg  = ""
        if not self.run_queue:
            self._set_fail("TEKRAR'dan önce yön komutu ekle!")
            return
        self.running = True

    # ── Çizim ─────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(BG)
        if self.scene == "menu":
            self._draw_menu()
        elif self.scene == "game":
            self._draw_game()
        elif self.scene == "win":
            self._draw_win()
        elif self.scene == "levelsel":
            self._draw_levelsel()
        self._present()
        pygame.display.flip()

    def _present(self):
        """Sanal tuvali cihaz ekranına ölçekleyerek bas (kenarlar siyah şerit)."""
        if self._sw == SCREEN_W and self._sh == SCREEN_H and self._ox == 0 and self._oy == 0:
            self.display.blit(self.screen, (0, 0))
        else:
            self.display.fill((0, 0, 0))
            # smoothscale yerine scale: mobilde çok daha hızlı (kasmayı önler)
            scaled = pygame.transform.scale(self.screen, (self._sw, self._sh))
            self.display.blit(scaled, (self._ox, self._oy))

    def _mouse_canvas(self):
        return self.to_canvas(pygame.mouse.get_pos())

    def to_canvas(self, pos):
        """Cihaz ekranı koordinatını sanal tuval koordinatına çevirir."""
        return ((pos[0] - self._ox) / self._scale, (pos[1] - self._oy) / self._scale)

    # ── Menü ──────────────────────────────────────────────────────────────────
    def _draw_menu(self):
        cx = SCREEN_W // 2

        # Başlık — şık font
        title_s = self.font_title_main.render("ROBOTO'YU KURTAR!", True, TITLE_C)
        self.screen.blit(title_s, (cx - title_s.get_width()//2, 70))

        # Alt başlık
        self._draw_subtitle("Komutları doğru düzenle ve Roboto'yu kurtar!", cx, 138)
        self._draw_subtitle("10-14 Yaş  ·  Mantık & Kodlama Bulmacası", cx, 162)

        # Robot sembolü — küçük glow halkası (yazılardan uzak)
        rx, ry, cell = cx - 35, 210, 70
        ticks = pygame.time.get_ticks()
        glow_a = int(((math.sin(ticks / 600) + 1) / 2) * 55 + 25)
        for spread, alpha in ((10, glow_a // 3), (6, glow_a // 2), (3, glow_a)):
            gs = pygame.Surface((cell + spread*2, cell + spread*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*ROBOT_C, alpha),
                               (cell//2 + spread, cell//2 + spread), cell//2 + spread)
            self.screen.blit(gs, (rx - spread, ry - spread))
        draw_robot(self.screen, rx, ry, 2, cell)

        # Yıldız (süre) kuralları kutusu — sol tarafta
        self._draw_score_rules()

        # Butonlar
        self._draw_button("OYNA",      cx - 120, 310, 240, 55, BTN_RUN)
        self._draw_button("BÖLÜM SEÇ", cx - 120, 410, 240, 55, BTN_STEP)

        # Yıldız toplamı
        total = sum(self.stars_earned)
        max_s = len(LEVELS) * 3
        t = self.font_med.render(f"Toplam Yıldız: {total} / {max_s}", True, STAR_ON)
        self.screen.blit(t, (cx - t.get_width()//2, 500))

        # Kronometre aç/kapa butonu
        tr  = self._timer_btn_rect()
        on  = self.timer_enabled
        lbl = "KRONOMETRE: AÇIK" if on else "KRONOMETRE: KAPALI"
        self._draw_button(lbl, tr.x, tr.y, tr.w, tr.h, (214, 82, 82) if on else WALL_C)

        # Müzik pause butonu (sağ üst)
        r = self._music_btn_rect()
        hovered = r.collidepoint(self._mouse_canvas())
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (*TEXT_C, 55 if hovered else 22), (0, 0, r.w, r.h), border_radius=10)
        pygame.draw.rect(bg, (*TEXT_C, 90), (0, 0, r.w, r.h), 1, border_radius=10)
        self.screen.blit(bg, r.topleft)
        ic = TEXT_C
        cx2, cy2 = r.centerx, r.centery
        if self.music_paused:
            pts = [(cx2 - 6, cy2 - 8), (cx2 - 6, cy2 + 8), (cx2 + 8, cy2)]
            pygame.draw.polygon(self.screen, ic, pts)
        else:
            pygame.draw.rect(self.screen, ic, (cx2 - 7, cy2 - 8, 5, 16))
            pygame.draw.rect(self.screen, ic, (cx2 + 2, cy2 - 8, 5, 16))

        # Tema (koyu/açık) butonu — sağ alt, küçük
        self._draw_theme_btn()

    def _draw_score_rules(self):
        """Menüde yıldız (süre) kurallarını gösteren kutu — sol taraf."""
        bx, by, bw, bh = 48, 300, 340, 200
        panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(panel, (*CARD_BG, 235), (0, 0, bw, bh), border_radius=14)
        pygame.draw.rect(panel, (*CYAN_C, 70), (0, 0, bw, bh), 1, border_radius=14)
        self.screen.blit(panel, (bx, by))

        ttl = self.font_med.render("YILDIZ KURALLARI", True, CYAN_C)
        self.screen.blit(ttl, (bx + bw // 2 - ttl.get_width() // 2, by + 14))
        sub = self.font_xs.render("Ne kadar hızlı bitirirsen o kadar çok yıldız!",
                                  True, TEXT_DARK)
        self.screen.blit(sub, (bx + bw // 2 - sub.get_width() // 2, by + 44))

        rows = [(3, "15 sn ve altı"), (2, "15 - 30 sn"), (1, "30 sn üzeri")]
        ry = by + 78
        for filled, label in rows:
            for s in range(3):
                draw_star(self.screen, bx + 34 + s * 26, ry + 9, 10, s < filled)
            txt = self.font_sm.render(label, True, TEXT_C)
            self.screen.blit(txt, (bx + 128, ry))
            ry += 40

    # ── Oyun sahnesi ──────────────────────────────────────────────────────────
    def _draw_game(self):
        lvl = LEVELS[self.level_idx]
        panel_x = SCREEN_W - PANEL_W

        # Sol: ızgara
        self._draw_grid(panel_x)

        # Sol alt: elle kontrol ok tuşları
        self._draw_dpad()

        # ── Panel ──────────────────────────────────────────────────────────────
        pygame.draw.rect(self.screen, PANEL_C, (panel_x, 0, PANEL_W, SCREEN_H))

        # ── Header (badge + title + hint + stars) ──────────────────────────────
        hdr = pygame.Rect(panel_x + 8, 8, PANEL_W - 18, 98)
        pygame.draw.rect(self.screen, CARD_BG, hdr, border_radius=12)
        pygame.draw.rect(self.screen, CARD_BD, hdr, 1, border_radius=12)

        # Bölüm badge (pill)
        badge_txt = f"Bölüm {self.level_idx+1} / {lvl['concept']}"
        badge_s   = self.font_xs.render(badge_txt, True, CYAN_C)
        bpad      = 10
        br        = pygame.Rect(panel_x + 16, 14, badge_s.get_width() + bpad*2, 18)
        bb        = pygame.Surface((br.w, br.h), pygame.SRCALPHA)
        pygame.draw.rect(bb, (*CYAN_C, 30),  (0, 0, br.w, br.h), border_radius=9)
        pygame.draw.rect(bb, (*CYAN_C, 64),  (0, 0, br.w, br.h), 1, border_radius=9)
        self.screen.blit(bb, br.topleft)
        self.screen.blit(badge_s, (br.x + bpad, br.y + (br.h - badge_s.get_height())//2))

        # Yıldızlar (sağ üst)
        for si in range(3):
            filled = si < self.stars_earned[self.level_idx]
            draw_star(self.screen, SCREEN_W - 26 - si * 34, 28, 12, filled)

        # Kronometre (yıldızların altında, sağa hizalı) — açıksa
        if self.timer_enabled:
            elapsed = self.solve_time if self.solve_time is not None \
                else (pygame.time.get_ticks() - self.timer_start)
            tcol = GOAL_C if self.solve_time is not None else CYAN_C
            self._draw_clock_time(SCREEN_W - 16, 56, elapsed, tcol)

        # Başlık
        title = self.font_med.render(lvl["title"], True, TEXT_C)
        self.screen.blit(title, (panel_x + 16, 38))

        # Açıklama — sol accent çizgisi + parlak renk
        hint_lines = self._wrap(lvl["hint"], 50)
        hint_color = CONCEPT_C.get(lvl["concept"], CYAN_C)
        total_hint_h = len(hint_lines) * 16
        pygame.draw.rect(self.screen, hint_color,
                         (panel_x + 16, 60, 2, total_hint_h), border_radius=1)
        for hi, line in enumerate(hint_lines):
            t = self.font_hint.render(line, True, TEXT_C)
            self.screen.blit(t, (panel_x + 22, 60 + hi * 18))

        # ── KOMUT EKLE ─────────────────────────────────────────────────────────
        lbl1_y = 115
        lbl1 = self.font_xs.render("+ KOMUT EKLE", True, CYAN_C)
        self.screen.blit(lbl1, (panel_x + 12, lbl1_y))
        hk = self.font_xs.render("[1-6]", True, (60, 75, 100))
        self.screen.blit(hk, (SCREEN_W - hk.get_width() - 8, lbl1_y))


        for i, cmd in enumerate(COMMANDS):
            r = self._cmd_btn_rect(i, panel_x)
            self._draw_cmd_btn(r, CMD_COLORS.get(cmd, BTN_STEP), cmd)

        # ── PROGRAM ────────────────────────────────────────────────────────────
        lbl2_y = 256
        lbl2 = self.font_xs.render(f"<> PROGRAM  ({len(self.commands)} komut)", True, CYAN_C)
        self.screen.blit(lbl2, (panel_x + 12, lbl2_y))
        if self.running or self.step_count > 0:
            sc = self.font_xs.render(f"adım: {self.step_count}", True, GOAL_C)
            self.screen.blit(sc, (SCREEN_W - sc.get_width() - 8, lbl2_y))

        # Program alanı (dashed border kutup)
        pa = pygame.Rect(panel_x + 8, 272, PANEL_W - 18, SCREEN_H - 272 - 64)
        pa_bg = pygame.Surface((pa.w, pa.h), pygame.SRCALPHA)
        pygame.draw.rect(pa_bg, (255, 255, 255, 10), (0, 0, pa.w, pa.h), border_radius=14)
        self.screen.blit(pa_bg, pa.topleft)
        pa_b = pygame.Surface((pa.w, pa.h), pygame.SRCALPHA)
        pygame.draw.rect(pa_b, (*CYAN_C, 50), (0, 0, pa.w, pa.h), 2, border_radius=14)
        self.screen.blit(pa_b, pa.topleft)

        # Boş durum
        if not self.commands:
            cy  = pa.y + pa.h // 2
            cx  = pa.centerx
            col = (58, 74, 107)
            # Robot kafası
            pygame.draw.rect(self.screen, col,
                             (cx - 18, cy - 34, 36, 30), border_radius=6)
            pygame.draw.rect(self.screen, (80, 105, 150),
                             (cx - 18, cy - 34, 36, 30), 1, border_radius=6)
            # Gözler
            pygame.draw.circle(self.screen, (100, 150, 210), (cx - 7, cy - 22), 4)
            pygame.draw.circle(self.screen, (100, 150, 210), (cx + 7, cy - 22), 4)
            # Ağız
            pygame.draw.rect(self.screen, (80, 115, 170),
                             (cx - 7, cy - 12, 14, 3), border_radius=1)
            # Anten
            pygame.draw.line(self.screen, col, (cx, cy - 34), (cx, cy - 42), 2)
            pygame.draw.circle(self.screen, (90, 130, 195), (cx, cy - 44), 3)
            # Gövde
            pygame.draw.rect(self.screen, col,
                             (cx - 14, cy - 4, 28, 18), border_radius=4)
            empty_txt = self.font_hint.render("Henüz komut yok…", True, (58, 74, 107))
            self.screen.blit(empty_txt, (cx - empty_txt.get_width()//2, cy + 20))

        # Chip'ler program kutusunun dışına taşmasın diye kırp
        clip_prev = self.screen.get_clip()
        self.screen.set_clip(pa.inflate(-4, -4))
        for i, cmd in enumerate(self.commands):
            base_r = self._prog_item_rect(i, panel_x)
            # Görünür bandın tamamen dışındaki chip'leri atla (performans)
            if base_r.bottom < pa.top or base_r.top > pa.bottom:
                continue

            # Bounce animasyonu
            elapsed = pygame.time.get_ticks() - self.last_added_time
            if i == self.last_added_idx and elapsed < 280:
                scale = 1.0 + 0.22 * math.sin(elapsed / 280 * math.pi)
                ix = int(base_r.w * (scale - 1))
                iy = int(base_r.h * (scale - 1))
                r = base_r.inflate(ix, iy)
            else:
                r = base_r

            color  = CMD_COLORS.get(cmd, BTN_STEP)
            active = self.running and (i == self.run_index - 1)

            # Gölge
            sh = pygame.Surface((r.w + 4, r.h + 5), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0, 0, 0, 55), sh.get_rect(), border_radius=r.h // 2 + 2)
            self.screen.blit(sh, (r.x + 2, r.y + 3))

            # Aktifse parlak çerçeve
            if active:
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 r.inflate(4, 4), 2, border_radius=r.h // 2 + 2)

            # Chip gövdesi — yumuşak gradient (sarı/turuncu çakmaması için +25)
            light = tuple(min(c + 25, 255) for c in color)
            dark  = tuple(max(c - 20, 0)   for c in color)
            self._smooth_gradient_rect(r, light, dark, radius=r.h // 2)

            # Sol: numara dairesi
            nr   = r.h // 2 - 2
            ncx  = r.x + nr + 3
            ncy  = r.centery
            dark = (max(color[0]-50, 0), max(color[1]-50, 0), max(color[2]-50, 0))
            pygame.draw.circle(self.screen, dark, (ncx, ncy), nr)
            ns = self.font_prog.render(str(i + 1), True, (255, 255, 255))
            self.screen.blit(ns, (ncx - ns.get_width() // 2, ncy - ns.get_height() // 2))

            # Sağ: X sil (elle çizilmiş) — sağ kenara yakın
            xc = r.right - 10
            xs = 4

            # İkon + etiket — numara dairesi ile X arasındaki alana ortalanır.
            # Sığmazsa (örn. uzun "YUKARI") etiket fontu küçülür, taşma olmaz.
            icon   = CMD_ICONS.get(cmd, "")
            # TEKRAR'larda "2×"/"3×" ikonu zaten anlamı taşıyor → metni tekrarlama
            label  = "" if cmd.startswith("TEKRAR") else cmd
            gap    = 3 if label else 0
            region_l = ncx + nr + 3
            region_r = xc - xs - 3
            region_w = region_r - region_l
            lab_font = self.font_prog
            icon_s   = lab_font.render(icon,  True, (255, 255, 255))
            label_s  = lab_font.render(label, True, (255, 255, 255))
            if icon_s.get_width() + gap + label_s.get_width() > region_w:
                lab_font = self.font_xs
                icon_s   = lab_font.render(icon,  True, (255, 255, 255))
                label_s  = lab_font.render(label, True, (255, 255, 255))
            group_w = icon_s.get_width() + gap + label_s.get_width()
            gx0 = region_l + max(0, (region_w - group_w) // 2)
            self.screen.blit(icon_s,  (gx0, ncy - icon_s.get_height() // 2))
            self.screen.blit(label_s, (gx0 + icon_s.get_width() + gap,
                                       ncy - label_s.get_height() // 2))

            pygame.draw.line(self.screen, (255, 170, 170), (xc - xs, ncy - xs), (xc + xs, ncy + xs), 2)
            pygame.draw.line(self.screen, (255, 170, 170), (xc + xs, ncy - xs), (xc - xs, ncy + xs), 2)

        self.screen.set_clip(clip_prev)

        # Kaydırma çubuğu (komutlar alana sığmadığında)
        self._clamp_prog_scroll()
        ms = self._prog_max_scroll()
        if ms > 0:
            track = pygame.Rect(pa.right - 9, pa.y + 6, 5, pa.h - 12)
            ts = pygame.Surface((track.w, track.h), pygame.SRCALPHA)
            pygame.draw.rect(ts, (*CYAN_C, 30), (0, 0, track.w, track.h), border_radius=3)
            self.screen.blit(ts, track.topleft)
            thumb_h = max(28, int(track.h * track.h / (track.h + ms)))
            thumb_y = track.y + int((track.h - thumb_h) * (self.prog_scroll / ms))
            tb = pygame.Surface((track.w, thumb_h), pygame.SRCALPHA)
            pygame.draw.rect(tb, (*CYAN_C, 170), (0, 0, track.w, thumb_h), border_radius=3)
            self.screen.blit(tb, (track.x, thumb_y))

        # Hata mesajı
        if self.fail_msg:
            fm = self.font_sm.render(self.fail_msg, True, (255, 100, 100))
            self.screen.blit(fm, (panel_x + 10, SCREEN_H - 90))

        # Aksiyon butonları
        act_y = SCREEN_H - 48
        # ÇALIŞTIR pulse halkası
        ticks = pygame.time.get_ticks()
        pulse = (math.sin(ticks / 320) + 1) / 2
        ps = int(pulse * 5) + 1
        pa2 = int(pulse * 120)
        run_r, clr_r, rst_r = self._action_btn_rects(panel_x)
        pr  = pygame.Rect(run_r[0] - ps, run_r[1] - ps, run_r[2] + ps*2, run_r[3] + ps*2)
        p_s = pygame.Surface((pr.w, pr.h), pygame.SRCALPHA)
        pygame.draw.rect(p_s, (*BTN_RUN, pa2), (0, 0, pr.w, pr.h), 2, border_radius=16)
        self.screen.blit(p_s, (pr.x, pr.y))

        self._draw_button("[C] ÇALIŞTIR", *run_r, BTN_RUN,   shadow=False)
        self._draw_button("[T] TEMİZLE",  *clr_r, BTN_CLEAR, shadow=False)
        self._draw_button("[Z] GERİ AL", *rst_r, BTN_RESET, shadow=False)

        # Geri
        mb = self._menu_back_rect()
        self._draw_button("← Menü", mb.x, mb.y, mb.w, mb.h, WALL_C, shadow=False)

    def _draw_grid(self, panel_x):
        grid  = self.grid
        rows  = len(grid)
        cols  = max(len(r) for r in grid)
        C     = self.cell          # bu level için hücre boyutu
        gx    = max(10, (panel_x - cols * C) // 2)
        gy    = max(10, (SCREEN_H - DPAD_H - rows * C) // 2)   # D-pad şeridi üstünde ortala
        self.grid_x = gx
        self.grid_y = gy

        for r, row in enumerate(grid):
            for c, ch in enumerate(row):
                x = gx + c * C
                y = gy + r * C
                if ch == "#":
                    pygame.draw.rect(self.screen, WALL_C, (x, y, C, C))
                    pygame.draw.rect(self.screen, BG, (x+1, y+1, C-2, C-2), 2)
                elif ch in (".", "S"):
                    pygame.draw.rect(self.screen, FLOOR_C, (x, y, C, C))
                    pygame.draw.rect(self.screen, GRID_BG, (x, y, C, C), 1)

        # Hedef
        gx2 = gx + self.goal[0] * C
        gy2 = gy + self.goal[1] * C
        pygame.draw.rect(self.screen, FLOOR_C, (gx2, gy2, C, C))
        # Roboto (hedef) — yuvarlak, tok renkli
        ccx, ccy = gx2 + C // 2, gy2 + C // 2
        rad = C // 2 - 5
        pygame.draw.circle(self.screen, GOAL_RING, (ccx, ccy), rad)
        pygame.draw.circle(self.screen, GOAL_FILL, (ccx, ccy), rad - 3)
        draw_star(self.screen, ccx, ccy, rad - 8, True, color=(70, 44, 10))

        # Robot
        draw_robot(self.screen, gx + self.robot.px, gy + self.robot.py,
                   self.robot.dir, C)

    # ── Kazandı ekranı ────────────────────────────────────────────────────────
    def _draw_win(self):
        self._draw_confetti()
        earned = self.stars_earned[self.level_idx]
        self._draw_title_text("TEBRİKLER! 🎉", SCREEN_W // 2, 160)
        msg = self.font_big.render(f"Bölüm {self.level_idx+1} tamamlandı!", True, TEXT_C)
        self.screen.blit(msg, (SCREEN_W//2 - msg.get_width()//2, 220))

        if self.timer_enabled and self.solve_time is not None:
            info = f"Adım: {self.step_count}    ·    Süre: {self._fmt_time(self.solve_time)}"
        else:
            info = f"Kullanılan adım: {self.step_count}"
        steps = self.font_med.render(info, True, TEXT_DARK)
        self.screen.blit(steps, (SCREEN_W//2 - steps.get_width()//2, 265))

        for i in range(3):
            draw_star(self.screen, SCREEN_W//2 - 80 + i * 80, 330, 36, i < earned)

        star_msg = ["", "İyi iş!", "Harika!", "Mükemmel!"][earned]
        sm = self.font_big.render(star_msg, True, STAR_ON)
        self.screen.blit(sm, (SCREEN_W//2 - sm.get_width()//2, 390))

        if self.level_idx < len(LEVELS) - 1:
            self._draw_button("Sonraki Bölüm →", SCREEN_W//2 - 130, 440, 260, 55, BTN_RUN)
        self._draw_button("Tekrar Oyna", SCREEN_W//2 - 130, 510, 260, 55, BTN_STEP)
        self._draw_button("Ana Menü",    SCREEN_W//2 - 130, 580, 260, 55, WALL_C)

    # ── Bölüm seçimi ──────────────────────────────────────────────────────────
    def _draw_levelsel(self):
        self._draw_title_text("BÖLÜM SEÇ", SCREEN_W // 2, 55)
        total = sum(self.stars_earned)
        ts = self.font_sm.render(f"Toplam: {total} / {len(LEVELS)*3} yıldız", True, STAR_ON)
        self.screen.blit(ts, (SCREEN_W//2 - ts.get_width()//2, 98))

        for i, lvl in enumerate(LEVELS):
            rect = self._levelsel_rect(i)
            rx, ry, bw, bh = rect.x, rect.y, rect.w, rect.h
            locked = not self._is_unlocked(i)
            c      = (45, 52, 70) if locked else CONCEPT_C.get(lvl["concept"], TEXT_C)
            bg_c   = CARD_LOCK if locked else CARD_BG
            pygame.draw.rect(self.screen, bg_c, rect, border_radius=10)
            pygame.draw.rect(self.screen, c,    rect, 2, border_radius=10)
            num_c   = (50, 60, 80) if locked else c
            title_c = (50, 60, 80) if locked else TEXT_C
            num = self.font_sm.render(str(i+1), True, num_c)
            self.screen.blit(num, (rx + 8, ry + 6))
            title = self.font_xs.render(lvl["title"][:15], True, title_c)
            self.screen.blit(title, (rx + bw//2 - title.get_width()//2, ry + 34))
            if locked:
                lx, ly = rx + bw - 20, ry + 8
                pygame.draw.rect(self.screen, (55, 65, 85), (lx - 5, ly + 5, 14, 10), border_radius=2)
                pygame.draw.arc(self.screen, (55, 65, 85),
                                pygame.Rect(lx - 3, ly, 10, 10), 0, math.pi, 2)
            else:
                for s in range(3):
                    filled = s < self.stars_earned[i]
                    draw_star(self.screen, rx + bw - 16 - s * 18, ry + 13, 7, filled)

        self._draw_button("← Geri", SCREEN_W//2 - 80, SCREEN_H - 50, 160, 38, WALL_C)

    # ── Yardımcılar ───────────────────────────────────────────────────────────
    def _cmd_btn_rect(self, i, panel_x):
        cols = 3
        gap  = 8
        bw   = (PANEL_W - 20 - (cols - 1) * gap) // cols
        bh   = 54
        c = i % cols
        r = i // cols
        x = panel_x + 10 + c * (bw + gap)
        y = 131 + r * (bh + 8)
        return pygame.Rect(x, y, bw, bh)

    def _prog_item_rect(self, i, panel_x):
        bw, bh, gap = 108, 28, 6
        c = i % PROG_COLS
        r = i // PROG_COLS
        x = panel_x + 10 + c * (bw + gap)
        y = PROG_Y0 + r * PROG_ROW_H - self.prog_scroll
        return pygame.Rect(x, y, bw, bh)

    @staticmethod
    def _prog_area_rect(panel_x):
        return pygame.Rect(panel_x + 8, 272, PANEL_W - 18, SCREEN_H - 272 - 64)

    def _prog_max_scroll(self):
        """Komut listesi alana sığmadığında kaydırılabilecek azami piksel."""
        rows = (len(self.commands) + PROG_COLS - 1) // PROG_COLS
        content_bottom = PROG_Y0 + max(0, rows - 1) * PROG_ROW_H + 28
        visible_bottom = (SCREEN_H - 64) - 8     # program alanı alt kenarı
        return max(0, content_bottom - visible_bottom)

    def _clamp_prog_scroll(self):
        self.prog_scroll = max(0, min(self.prog_scroll, self._prog_max_scroll()))

    def _add_command(self, cmd):
        if len(self.commands) < LEVELS[self.level_idx]["max_commands"]:
            self.commands.append(cmd)
            self.last_added_idx  = len(self.commands) - 1
            self.last_added_time = pygame.time.get_ticks()
            self.add_sound.play()
            self.prog_scroll = self._prog_max_scroll()   # en son komuta kaydır

    @staticmethod
    def _btn_rect(x, y, w, h):
        return pygame.Rect(x, y, w, h)

    @staticmethod
    def _menu_back_rect():
        # Sol alt köşe — grid ile çakışmaz (grid D-pad şeridinin üstünde kalır)
        return pygame.Rect(10, SCREEN_H - 44, 96, 32)

    @staticmethod
    def _levelsel_rect(i):
        # 8 sütunlu ızgara — 45 bölüm 6 satıra sığar
        cols_n, bw, bh, gap = 8, 142, 66, 8
        sx = (SCREEN_W - cols_n * (bw + gap)) // 2
        sy = 118
        return pygame.Rect(sx + (i % cols_n) * (bw + gap),
                           sy + (i // cols_n) * (bh + gap), bw, bh)

    @staticmethod
    def _dpad_rects():
        """Sol alttaki ok tuşları (D-pad) — yön → buton dikdörtgeni."""
        cxd = (SCREEN_W - PANEL_W) // 2
        s, p = 46, 52
        cyd = SCREEN_H - 8 - (p + s // 2)   # çapraz tuşları alta yasla (üstte etikete yer kalsın)
        return {
            "YUKARI": pygame.Rect(cxd - s // 2,     cyd - p - s // 2, s, s),
            "AŞAĞI":  pygame.Rect(cxd - s // 2,     cyd + p - s // 2, s, s),
            "SOLA":   pygame.Rect(cxd - p - s // 2, cyd - s // 2,     s, s),
            "SAĞA":   pygame.Rect(cxd + p - s // 2, cyd - s // 2,     s, s),
        }

    def _draw_dpad(self):
        cxd = (SCREEN_W - PANEL_W) // 2
        lbl = self.font_sm.render("OK veya WASD İLE OYNA", True, CYAN_C)
        self.screen.blit(lbl, (cxd - lbl.get_width() // 2, SCREEN_H - DPAD_H + 6))
        mouse = self._mouse_canvas()
        down  = pygame.mouse.get_pressed()[0]
        for cmd, r in self._dpad_rects().items():
            color = CMD_COLORS[cmd]
            hov   = r.collidepoint(mouse)
            dr    = r.move(0, 2) if (hov and down) else r
            bot   = tuple(max(c - 35, 0) for c in color)
            self._smooth_gradient_rect(dr, color, bot, radius=12)
            if hov and not down:
                hl = pygame.Surface((dr.w, dr.h), pygame.SRCALPHA)
                pygame.draw.rect(hl, (255, 255, 255, 30), (0, 0, dr.w, dr.h), border_radius=12)
                self.screen.blit(hl, dr.topleft)
            ic = self.font_big.render(CMD_ICONS[cmd], True, (255, 255, 255))
            self.screen.blit(ic, (dr.centerx - ic.get_width() // 2,
                                  dr.centery - ic.get_height() // 2))

    @staticmethod
    def _action_btn_rects(panel_x):
        """ÇALIŞTIR / TEMİZLE / BAŞA DÖN butonlarını panel genişliğine yayar."""
        act_y = SCREEN_H - 48
        gap   = 8
        bw    = (PANEL_W - 20 - 2 * gap) // 3
        x0    = panel_x + 10
        return (
            (x0,                  act_y, bw, 30),
            (x0 + (bw + gap),     act_y, bw, 30),
            (x0 + 2 * (bw + gap), act_y, bw, 30),
        )

    def _gradient_rect(self, surf, rect, color, radius=10):
        r, g, b = color
        top_c = (min(r+60,255), min(g+60,255), min(b+60,255))
        bot_c = (max(r-25,0),   max(g-25,0),   max(b-25,0))
        pygame.draw.rect(surf, bot_c, rect, border_radius=radius)
        th = rect.h // 2 + 4
        hl = pygame.Surface((rect.w, th), pygame.SRCALPHA)
        pygame.draw.rect(hl, (*top_c, 255), (0, 0, rect.w, th), border_radius=radius)
        pygame.draw.rect(hl, (*top_c, 255), (0, max(th-6,0), rect.w, 6))
        surf.blit(hl, (rect.x, rect.y))

    def _smooth_gradient_rect(self, rect, top_c, bot_c, radius=14):
        """Yumuşak dikey gradient, yuvarlak köşeli — üretilen yüzey önbelleğe alınır.
        (Aynı boyut+renk her karede yeniden hesaplanmaz; mobilde kasmayı önler.)"""
        key = (rect.w, rect.h, tuple(top_c), tuple(bot_c), radius)
        s = self._grad_cache.get(key)
        if s is None:
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            for y in range(rect.h):
                t  = y / max(rect.h - 1, 1)
                cr = int(top_c[0] + (bot_c[0] - top_c[0]) * t)
                cg = int(top_c[1] + (bot_c[1] - top_c[1]) * t)
                cb = int(top_c[2] + (bot_c[2] - top_c[2]) * t)
                pygame.draw.line(s, (cr, cg, cb, 255), (0, y), (rect.w - 1, y))
            mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, 255),
                             (0, 0, rect.w, rect.h), border_radius=radius)
            s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self._grad_cache[key] = s
        self.screen.blit(s, rect.topleft)

    def _draw_button(self, text, x, y, w, h, color, shadow=True):
        mouse_pos  = self._mouse_canvas()
        mouse_down = pygame.mouse.get_pressed()[0]
        base_rect  = pygame.Rect(x, y, w, h)
        hovered    = base_rect.collidepoint(mouse_pos)
        pressed    = hovered and mouse_down
        shadow_c   = tuple(max(v - 70, 0) for v in color)
        bot_c      = tuple(max(v - 35, 0) for v in color)
        sh_h, rad  = 4, 14

        # 3D alt gölge (shadow=False ise çizilmez)
        if shadow and not pressed:
            sh_r = pygame.Rect(x, y + h, w, sh_h)
            pygame.draw.rect(self.screen, shadow_c, sh_r, border_radius=rad)

        if pressed:
            dr = pygame.Rect(x, y + sh_h, w, h)
        elif hovered:
            dr = pygame.Rect(x, y - 1, w, h)
        else:
            dr = base_rect

        # Smooth gradient gövde
        self._smooth_gradient_rect(dr, color, bot_c, radius=rad)

        if hovered and not pressed:
            hl = pygame.Surface((dr.w, dr.h), pygame.SRCALPHA)
            pygame.draw.rect(hl, (255, 255, 255, 30), (0, 0, dr.w, dr.h), border_radius=rad)
            self.screen.blit(hl, dr.topleft)

        t = self.font_med.render(text, True, (255, 255, 255))
        self.screen.blit(t, (dr.centerx - t.get_width() // 2,
                              dr.centery - t.get_height() // 2))

    def _draw_cmd_btn(self, rect, color, text):
        mouse_pos  = self._mouse_canvas()
        mouse_down = pygame.mouse.get_pressed()[0]
        hovered    = rect.collidepoint(mouse_pos)
        pressed    = hovered and mouse_down
        bot_c      = CMD_BOT.get(text, tuple(max(v-40,0) for v in color))
        shadow_c   = color          # shadow = butonun ana rengi → parlak görünür
        sh_h, rad  = 5, 14

        # ── 3D alt renkli çizgi (kutu gölgesi) ───────────────────
        if not pressed:
            sh_r = pygame.Rect(rect.x, rect.y + rect.h, rect.w, sh_h)
            pygame.draw.rect(self.screen, shadow_c, sh_r, border_radius=rad)

        # Konum
        if pressed:
            dr = rect.move(0, sh_h)
        elif hovered:
            dr = rect.move(0, -2)
        else:
            dr = rect

        # ── Smooth gradient gövde ────────────────────────────────
        self._smooth_gradient_rect(dr, color, bot_c, radius=rad)

        # Hover parlaması
        if hovered and not pressed:
            hl = pygame.Surface((dr.w, dr.h), pygame.SRCALPHA)
            pygame.draw.rect(hl, (255, 255, 255, 30), (0, 0, dr.w, dr.h), border_radius=rad)
            self.screen.blit(hl, dr.topleft)

        # ── İkon (ortada-üst) ────────────────────────────────────
        icon   = CMD_ICONS.get(text, "")
        icon_s = self.font_med.render(icon, True, (255, 255, 255))
        self.screen.blit(icon_s, (dr.centerx - icon_s.get_width() // 2,
                                   dr.y + dr.h // 2 - icon_s.get_height() - 2))

        # ── Etiket (altta) ────────────────────────────────────────
        label_s = self.font_sm.render(text, True, (255, 255, 255))
        self.screen.blit(label_s, (dr.centerx - label_s.get_width() // 2,
                                    dr.y + dr.h // 2 + 3))

        # ── Tuş badge (belirgin pill) ─────────────────────────────
        key_str  = CMD_KEYS.get(text, "")
        key_s    = self.font_badge.render(key_str, True, (255, 255, 255))
        bw2      = max(key_s.get_width() + 12, 22)
        bh2      = key_s.get_height() + 6
        bx       = dr.right - bw2 - 3
        by       = dr.y + 3
        # Koyu dolgulu yuvarlak badge
        pygame.draw.rect(self.screen, (0, 0, 0),
                         (bx, by, bw2, bh2), border_radius=bh2 // 2)
        pygame.draw.rect(self.screen, (200, 215, 255),
                         (bx, by, bw2, bh2), 1, border_radius=bh2 // 2)
        self.screen.blit(key_s, (bx + (bw2 - key_s.get_width()) // 2,
                                  by + (bh2 - key_s.get_height()) // 2))

    def _draw_title_text(self, text, cx, y):
        t = self.font_title.render(text, True, TITLE_C)
        self.screen.blit(t, (cx - t.get_width()//2, y))

    def _draw_subtitle(self, text, cx, y):
        t = self.font_med.render(text, True, TEXT_DARK)
        self.screen.blit(t, (cx - t.get_width()//2, y))

    @staticmethod
    def _wrap(text, max_chars):
        words = text.split()
        lines, line = [], ""
        for w in words:
            if len(line) + len(w) + 1 <= max_chars:
                line += ("" if not line else " ") + w
            else:
                if line:
                    lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines


if __name__ == "__main__":
    Game().run()
