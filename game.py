import pygame
import math
import sys
import random
import array
import os

# --- CẤU HÌNH ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# MÀU SẮC
COLOR_BG = (5, 5, 8)                
COLOR_ENERGY = (0, 255, 255)        
COLOR_SILVER = (192, 192, 192)      
COLOR_SILVER_GLOW = (200, 200, 255)
COLOR_CRATE_BORDER = (80, 80, 90)
COLOR_RADAR_BG = (0, 20, 0)
COLOR_RADAR_LINE = (0, 80, 0)
COLOR_RADAR_ENEMY = (255, 0, 0)
COLOR_VICTORY_TEXT = (255, 215, 0)

# MÀU ROBOT MỚI
COLOR_MECH_PRIMARY = (10, 20, 30) 
COLOR_MECH_SEC = (100, 120, 130)  
COLOR_MECH_NEON = (0, 255, 255)   
COLOR_MECH_EYES = (0, 255, 255)   
COLOR_THRUSTER = (255, 100, 0)    
COLOR_CORE_HOT = (255, 200, 0)    

COLOR_BAR_BG = (50, 50, 50)        
COLOR_SLASH = (255, 255, 255)      
COLOR_GATE_GLOW = (255, 140, 0)    
COLOR_GATE_METAL = (70, 70, 80)    
COLOR_ORBITAL_BEAM = (100, 255, 255) 
COLOR_WARNING_RED = (255, 0, 0)

# GAMEPLAY
PLAYER_SPEED = 200
PLAYER_RUN_SPEED = 350
DASH_SPEED = 700
DASH_COOLDOWN = 3.5 # Giây
MONSTER_BASE_SPEED = 55
TRIGGER_COUNT = 3
RADAR_DETECTION_RANGE = 450
MAX_ENERGY = 10
SILVER_CRATE_CHANCE = 0.25 
GAME_DURATION = 60 # 60 Giây đếm ngược

# --- HỆ THỐNG ÂM THANH ---
def generate_sound(frequency=440, duration=0.1, volume=0.5, type="sine"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    max_vol = 32767 * volume
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = 0
        if type == "sine":
            val = math.sin(2 * math.pi * frequency * t)
        elif type == "noise":
            val = random.uniform(-1, 1)
        elif type == "saw":
            val = 2 * (t * frequency - math.floor(0.5 + t * frequency))
        elif type == "drone": 
            val = (math.sin(2 * math.pi * 50 * t) + 
                   math.sin(2 * math.pi * 55 * t) * 0.5 + 
                   random.uniform(-0.1, 0.1)) * 0.5
        elif type == "emp":
            val = math.sin(2 * math.pi * (800 - t * 3000) * t) * random.uniform(0.5, 1.0)
        elif type == "dash":
            val = math.sin(2 * math.pi * (300 + t * 1200) * t) * 0.8
        elif type == "heartbeat":
            p = (math.sin(2 * math.pi * 2.5 * t) ** 14)
            val = math.sin(2 * math.pi * 45 * t) * p
        buf[i] = int(val * max_vol)
    return pygame.mixer.Sound(buffer=buf)

def generate_spooky_horror_bgm(duration=10.0):
    """Tạo bản nhạc nền ma mị u uất, rùng rợn chuẩn Sci-Fi Horror bằng thuật toán tổng hợp âm thanh"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * n_samples)
    max_vol = 32767 * 0.38
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        
        # 1. Quỷ Tritone Dissonant Sub-Bass Drone (41.5 Hz + 58.7 Hz)
        drone = math.sin(2 * math.pi * 41.5 * t) * 0.45 + math.sin(2 * math.pi * 58.7 * t) * 0.35
        
        # 2. Tiếng nhịp tim thì thầm đập âm u
        heartbeat_pulse = (math.sin(2 * math.pi * 0.75 * t) ** 16) * 0.4
        sub_thud = math.sin(2 * math.pi * 36.0 * t) * heartbeat_pulse
        
        # 3. Tiếng chuông rít kim loại rùng rợn bí ẩn (High Pitch Dissonance)
        eerie_lfo = (math.sin(2 * math.pi * 0.12 * t) + 1.0) * 0.5
        high_pitch = (math.sin(2 * math.pi * 1850 * t) + math.sin(2 * math.pi * 1960 * t)) * 0.05 * eerie_lfo
        
        # 4. Tiếng gió đêm hư vô
        wind = random.uniform(-0.15, 0.15) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.06 * t))
        
        val = drone + sub_thud + high_pitch + wind
        val = max(-1.0, min(1.0, val))
        buf[i] = int(val * max_vol)
        
    return pygame.mixer.Sound(buffer=buf)

# --- KHỞI TẠO ---
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UEH: THE VOID LOGISTICS")
clock = pygame.time.Clock()

# --- TẠO ÂM THANH ---
try:
    snd_blip = generate_sound(880, 0.05, 0.1, "sine")
    snd_alert = generate_sound(150, 0.5, 0.3, "saw")
    snd_scream = generate_sound(0, 1.0, 0.8, "noise") 
    snd_open_good = generate_sound(1200, 0.1, 0.4, "sine") 
    snd_open_bad = generate_sound(200, 0.2, 0.4, "saw")
    snd_slash = generate_sound(0, 0.3, 0.6, "noise")
    snd_shield_break = generate_sound(100, 0.4, 0.7, "saw") 
    snd_equip = generate_sound(600, 0.1, 0.5, "sine")
    snd_gate_alarm = generate_sound(400, 0.5, 0.5, "saw")
    snd_orbital_charge = generate_sound(800, 1.5, 0.4, "sine")
    snd_orbital_boom = generate_sound(100, 4.0, 0.9, "noise") 
    snd_glitch = generate_sound(500, 0.1, 0.5, "noise")
    snd_time_bonus = generate_sound(1500, 0.2, 0.5, "sine")
    
    # ÂM THANH MỚI
    snd_dash = generate_sound(0, 0.15, 0.5, "dash")
    snd_emp = generate_sound(0, 0.3, 0.6, "emp")
    snd_heartbeat = generate_sound(0, 0.4, 0.6, "heartbeat")
    
    # --- TẢI NHẠC GAME TỪ FILE HOẶC TẠO NHẠC MA MỊ MỚI ---
    if os.path.isfile("nhac_game.ogg"):
        bg_music = pygame.mixer.Sound("nhac_game.ogg")
        bg_music.set_volume(0.5)
    else:
        bg_music = generate_spooky_horror_bgm(10.0)

except:
    snd_blip = None; snd_alert = None; snd_scream = None; snd_open_good = None
    snd_open_bad = None; snd_slash = None; snd_shield_break = None; snd_equip = None
    snd_dash = None; snd_emp = None; snd_heartbeat = None
    bg_music = generate_spooky_horror_bgm(10.0)
    snd_gate_alarm = None; snd_orbital_charge = None; snd_orbital_boom = None; snd_glitch = None; snd_time_bonus = None

# --- ASSETS ---
def load_image_safe(filename):
    fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fallback.fill((10, 10, 20))
    if not os.path.isfile(filename): return fallback
    try:
        img = pygame.image.load(filename).convert_alpha()
        return img 
    except: return fallback

bg_intro_img = load_image_safe("bg_intro.png")
if isinstance(bg_intro_img, pygame.Surface) and bg_intro_img.get_width() != SCREEN_WIDTH:
     bg_intro_img = pygame.transform.scale(bg_intro_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

bg_gameover_img = load_image_safe("bg_gameover.jpg")
if isinstance(bg_gameover_img, pygame.Surface) and bg_gameover_img.get_width() != SCREEN_WIDTH:
    bg_gameover_img = pygame.transform.scale(bg_gameover_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

ueh_logo_img = load_image_safe("image_74912d.png") 

def get_font(name, size, bold=False):
    return pygame.font.SysFont(name, size, bold=bold)

font_ui = get_font("consolas", 20)
font_big = get_font("impact", 80)
font_scary = get_font("chiller", 120, bold=True)
if not pygame.font.match_font("chiller"): font_scary = get_font("couriernew", 90, bold=True)
font_victory = get_font("arial", 70, bold=True) 
font_popup = get_font("consolas", 24, bold=True)
font_gate = get_font("arial", 18, bold=True)
font_glitch = get_font("impact", 110)
font_digital = get_font("impact", 40)
font_story = get_font("arial", 22) 

# --- CLASSES ---
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.stamina = 100
        self.angle = 0 
        self.has_scythe = False 
        self.emp_charges = 1 # Khởi đầu có sẵn 1 Mìn EMP
        self.dash_cd = 0.0
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_dir = (0, 0)
        self.afterimages = []
        self.original_image = pygame.Surface((70, 80), pygame.SRCALPHA)
        self.draw_elite_mech(self.original_image)
        self.is_exhausted = False 

    def draw_elite_mech(self, surface):
        w, h = 70, 80
        cx, cy = w//2, h//2
        pygame.draw.rect(surface, (30, 30, 30), (cx - 20, h - 20, 12, 20))
        pygame.draw.rect(surface, (30, 30, 30), (cx + 8, h - 20, 12, 20))  
        pygame.draw.polygon(surface, (255, 50, 0), [(cx - 20, h), (cx - 14, h + 15), (cx - 8, h)])
        pygame.draw.polygon(surface, (255, 50, 0), [(cx + 8, h), (cx + 14, h + 15), (cx + 20, h)])
        body_points = [(cx - 12, 15), (cx + 12, 15), (cx + 18, 25), (cx + 15, 60), (cx, 70), (cx - 15, 60), (cx - 18, 25)]
        pygame.draw.polygon(surface, COLOR_MECH_PRIMARY, body_points)
        pygame.draw.polygon(surface, COLOR_MECH_SEC, body_points, 2)
        pygame.draw.polygon(surface, COLOR_MECH_PRIMARY, [(cx-15, 25), (cx-32, 20), (cx-32, 45), (cx-15, 40)])
        pygame.draw.polygon(surface, COLOR_MECH_SEC, [(cx-15, 25), (cx-32, 20), (cx-32, 45), (cx-15, 40)], 2)
        pygame.draw.polygon(surface, COLOR_MECH_PRIMARY, [(cx+15, 25), (cx+32, 20), (cx+32, 45), (cx+15, 40)])
        pygame.draw.polygon(surface, COLOR_MECH_SEC, [(cx+15, 25), (cx+32, 20), (cx+32, 45), (cx+15, 40)], 2)
        pygame.draw.circle(surface, (50, 50, 60), (cx, 40), 10) 
        pygame.draw.circle(surface, COLOR_CORE_HOT, (cx, 40), 6) 
        head_rect = pygame.Rect(cx - 9, 8, 18, 20)
        pygame.draw.rect(surface, (50, 50, 60), head_rect)
        pygame.draw.rect(surface, COLOR_MECH_SEC, head_rect, 1)
        pygame.draw.line(surface, COLOR_MECH_EYES, (cx - 7, 12), (cx, 18), 2)
        pygame.draw.line(surface, COLOR_MECH_EYES, (cx + 7, 12), (cx, 18), 2)

    def move(self, keys, dt):
        if self.dash_cd > 0: self.dash_cd -= dt

        input_x = 0; input_y = 0
        if keys[pygame.K_w]: input_y -= 1
        if keys[pygame.K_s]: input_y += 1
        if keys[pygame.K_a]: input_x -= 1
        if keys[pygame.K_d]: input_x += 1

        if input_x != 0 or input_y != 0:
            length = math.hypot(input_x, input_y)
            input_x /= length; input_y /= length
            self.angle = math.degrees(math.atan2(-input_y, input_x)) - 90

        # Kích hoạt Cyber Dash (Phím SPACE)
        if keys[pygame.K_SPACE] and self.dash_cd <= 0 and not self.is_exhausted and (input_x != 0 or input_y != 0):
            self.is_dashing = True
            self.dash_timer = 0.18
            self.dash_cd = DASH_COOLDOWN
            self.dash_dir = (input_x, input_y)
            if snd_dash: snd_dash.play()

        # Xử lý khi đang Lướt (Dash)
        if self.is_dashing:
            self.dash_timer -= dt
            self.x += self.dash_dir[0] * DASH_SPEED * dt
            self.y += self.dash_dir[1] * DASH_SPEED * dt
            self.afterimages.append({"x": self.x, "y": self.y, "angle": self.angle, "alpha": 200})
            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            speed_mult = 0.2 if self.is_exhausted else 1.0
            if input_x != 0 or input_y != 0:
                current_speed = PLAYER_SPEED * speed_mult
                if keys[pygame.K_LSHIFT] and self.stamina > 0 and not self.is_exhausted:
                    current_speed = PLAYER_RUN_SPEED
                    self.stamina -= 30 * dt
                self.x += input_x * current_speed * dt
                self.y += input_y * current_speed * dt
            if not keys[pygame.K_LSHIFT] and self.stamina < 100: 
                self.stamina += 15 * dt

        # Cập nhật tàn ảnh ma quái (Afterimages)
        for img in self.afterimages[:]:
            img["alpha"] -= 1200 * dt
            if img["alpha"] <= 0: self.afterimages.remove(img)

        self.x = max(30, min(SCREEN_WIDTH - 30, self.x))
        self.y = max(30, min(SCREEN_HEIGHT - 30, self.y))

class EmpTrap:
    """Bẫy Mìn EMP Tê Liệt Quái Vật"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.pulse = 0.0

    def draw(self, surface):
        if not self.active: return
        self.pulse += 0.1
        r = 16 + math.sin(self.pulse) * 4
        pygame.draw.circle(surface, (0, 100, 255), (int(self.x), int(self.y)), int(r), 2)
        pygame.draw.circle(surface, (0, 255, 255), (int(self.x), int(self.y)), 6)

class FogParticle:
    """Hệ thống Sương mù u uất ma mị"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.radius = random.randint(80, 160)
        self.alpha = random.randint(15, 35)
        self.speed = random.uniform(5, 15)

    def update(self, dt):
        self.x += self.speed * dt
        if self.x - self.radius > SCREEN_WIDTH:
            self.x = -self.radius
            self.y = random.randint(0, SCREEN_HEIGHT)

    def draw(self, surface):
        fog_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(fog_surf, (20, 25, 35, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(fog_surf, (self.x - self.radius, self.y - self.radius))

class Monster:
    def __init__(self):
        self.x = 50; self.y = 50
        self.active = False
        self.speed = MONSTER_BASE_SPEED
        self.anim_offset = 0
        self.frenzy_mode = False
        self.stun_timer = 0.0 # Thời gian dính bẫy tê liệt
     
    def hunt(self, p_x, p_y, dt):
        if self.active:
            if self.stun_timer > 0:
                self.stun_timer -= dt
                return

            dx, dy = p_x - self.x, p_y - self.y
            dist = math.hypot(dx, dy)
            current_speed = self.speed
            if self.frenzy_mode: current_speed = 600 
            
            if dist > 0:
                move_dist = current_speed * dt
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
            self.anim_offset += dt * 5

class LootCrate:
    def __init__(self, current_score, force_normal=False):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.type = "NORMAL"
        self.is_empty = False
        self.has_time_bonus = False 
        
        if current_score >= 2 and not force_normal:
            if random.random() < SILVER_CRATE_CHANCE: 
                self.type = "SILVER"
                if current_score >= 7 and random.random() < 0.5: 
                    self.has_time_bonus = True

        if self.type == "NORMAL":
            if current_score >= 6:
                if random.random() < 0.6: self.is_empty = True
            else:
                self.is_empty = False 

class DeliveryGate:
    def __init__(self):
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
        self.active = False
        self.pulse = 0
        self.is_locked = False 

# --- DRAWING ---

def draw_ueh_logo(surface, x, y):
    if isinstance(ueh_logo_img, pygame.Surface) and ueh_logo_img.get_width() > 10:
        target_width = 250
        ratio = ueh_logo_img.get_width() / ueh_logo_img.get_height()
        target_height = int(target_width / ratio)
        scaled_logo = pygame.transform.scale(ueh_logo_img, (target_width, target_height))
        rect = scaled_logo.get_rect(center=(x, y))
        surface.blit(scaled_logo, rect)
    else:
        pygame.draw.rect(surface, (0, 50, 150), (x - 60, y - 30, 120, 60))
        txt = font_ui.render("UEH LOGO", True, (255, 255, 255))
        surface.blit(txt, (x - 40, y - 10))

def draw_scifi_crate(surface, x, y, type, has_time_bonus):
    size = 34
    rect = pygame.Rect(x - size//2, y - size//2, size, size)
    rect.y += math.sin(pygame.time.get_ticks() / 150) * 4
    
    is_silver = (type == "SILVER")
    if is_silver:
        main_color = (180, 180, 190)
        border_color = (255, 255, 255)
        if has_time_bonus:
            final_glow = (255, 215, 0) 
            glow_intensity = abs(math.sin(pygame.time.get_ticks() / 100)) 
        else:
            final_glow = (255, 255, 255)
            glow_intensity = abs(math.sin(pygame.time.get_ticks() / 200))
    else:
        main_color = (40, 40, 50)
        border_color = COLOR_CRATE_BORDER
        glow_intensity = abs(math.sin(pygame.time.get_ticks() / 200))
        final_glow = (0, int(255 * glow_intensity), int(255 * glow_intensity))

    pygame.draw.rect(surface, main_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    center_rect = rect.inflate(-12, -12)
    
    pygame.draw.rect(surface, final_glow, center_rect)
    
    pygame.draw.line(surface, border_color, rect.topleft, rect.bottomright, 2)
    pygame.draw.line(surface, border_color, rect.topright, rect.bottomleft, 2)

def draw_delivery_gate_advanced(surface, gate):
    if not gate.active and not gate.is_locked: return
    
    if gate.is_locked:
        base_radius = 70
        pygame.draw.circle(surface, (50, 0, 0), (gate.x, gate.y), base_radius + 10)
        pygame.draw.line(surface, (255, 0, 0), (gate.x - 50, gate.y - 50), (gate.x + 50, gate.y + 50), 5)
        pygame.draw.line(surface, (255, 0, 0), (gate.x + 50, gate.y - 50), (gate.x - 50, gate.y + 50), 5)
        text_surf = font_gate.render("GATE LOCKED - TIMEOUT", True, (255, 0, 0))
        text_rect = text_surf.get_rect(center=(gate.x, gate.y - 90))
        surface.blit(text_surf, text_rect)
        return

    gate.pulse += 0.05
    base_radius = 70
    pygame.draw.circle(surface, COLOR_GATE_METAL, (gate.x, gate.y), base_radius + 10)
    pygame.draw.circle(surface, (30, 30, 40), (gate.x, gate.y), base_radius + 5, 3)
    num_rings = 3
    for i in range(num_rings):
        angle_offset = gate.pulse * (i + 1) * 0.5
        ring_radius = base_radius - (i * 10)
        pygame.draw.circle(surface, COLOR_CRATE_BORDER, (gate.x, gate.y), int(ring_radius), 2)
        px = gate.x + math.cos(angle_offset) * ring_radius
        py = gate.y + math.sin(angle_offset) * ring_radius
        pygame.draw.circle(surface, COLOR_GATE_GLOW, (px, py), 5)
    beam_width = 40 + math.sin(gate.pulse * 2) * 5
    beam_rect = pygame.Rect(gate.x - beam_width//2, gate.y - 100, beam_width, 120)
    glow_surf = pygame.Surface((beam_width + 20, 140), pygame.SRCALPHA)
    pygame.draw.ellipse(glow_surf, (*COLOR_GATE_GLOW, 100), glow_surf.get_rect())
    surface.blit(glow_surf, (gate.x - beam_width//2 - 10, gate.y - 110))
    pygame.draw.ellipse(surface, (255, 255, 200), beam_rect)
    pygame.draw.ellipse(surface, COLOR_GATE_GLOW, beam_rect, 5)
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        text_surf = font_gate.render("DELIVER CARGO HERE", True, COLOR_GATE_GLOW)
        text_rect = text_surf.get_rect(center=(gate.x, gate.y - 120))
        holo_bg = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
        holo_bg.fill((*COLOR_GATE_GLOW, 50)) 
        surface.blit(holo_bg, (text_rect.x - 10, text_rect.y - 5))
        surface.blit(text_surf, text_rect)

def draw_player_avatar(surface, player):
    # Vẽ tàn ảnh lướt (Afterimages)
    for img in player.afterimages:
        rot = pygame.transform.rotate(player.original_image, img["angle"])
        rot.set_alpha(max(0, int(img["alpha"])))
        r = rot.get_rect(center=(img["x"], img["y"]))
        surface.blit(rot, r)

    rotated_image = pygame.transform.rotate(player.original_image, player.angle)
    rect = rotated_image.get_rect(center=(player.x, player.y))
    
    if player.is_exhausted:
        rotated_image.fill((100, 0, 0, 255), special_flags=pygame.BLEND_ADD)
    
    surface.blit(rotated_image, rect)
    
    if player.has_scythe:
        angle = (pygame.time.get_ticks() / 5) % 360
        r = 50 
        rad = math.radians(angle)
        pygame.draw.circle(surface, (150, 255, 255), (int(player.x), int(player.y)), r, 1)
        for i in range(3):
            oa = rad + (i * 2.09) 
            ox = player.x + math.cos(oa) * r
            oy = player.y + math.sin(oa) * r
            pygame.draw.line(surface, (255, 255, 255), (ox-5, oy-5), (ox+5, oy+5), 2)

def draw_spectral_monster(surface, monster, scale=1.0, is_dying=False):
    x, y, anim_offset = monster.x, monster.y, monster.anim_offset
    pulse = math.sin(anim_offset) * 5 * scale
    aura_surf = pygame.Surface((int(100*scale), int(100*scale)), pygame.SRCALPHA)
    pygame.draw.circle(aura_surf, (50, 0, 20, 50), (int(50*scale), int(50*scale)), int((40 + pulse)*scale))
    surface.blit(aura_surf, (x - 50*scale, y - 50*scale))
    mid_surf = pygame.Surface((int(80*scale), int(80*scale)), pygame.SRCALPHA)
    pygame.draw.circle(mid_surf, (80, 0, 0, 100), (int(40*scale), int(40*scale)), int((25 + pulse/2)*scale))
    surface.blit(mid_surf, (x - 40*scale, y - 40*scale))
    num_tentacles = 6
    for i in range(num_tentacles):
        angle = (pygame.time.get_ticks() / 200) + (i * (6.28 / num_tentacles))
        tx = x + math.cos(angle) * (20 * scale)
        ty = y + math.sin(angle) * (20 * scale)
        ex = x + math.cos(angle) * (50 * scale + pulse)
        ey = y + math.sin(angle) * (50 * scale + pulse)
        pygame.draw.line(surface, (30, 0, 0), (tx, ty), (ex, ey), int(3*scale))
    
    if monster.stun_timer > 0:
        # Tia điện giật khi bị tê liệt bởi Mìn EMP
        for _ in range(5):
            sx = x + random.randint(-25, 25)
            sy = y + random.randint(-25, 25)
            ex = x + random.randint(-25, 25)
            ey = y + random.randint(-25, 25)
            pygame.draw.line(surface, (0, 255, 255), (sx, sy), (ex, ey), 2)

    if not is_dying:
        core_rect = pygame.Rect(x - 10*scale, y - 10*scale, 20*scale, 20*scale)
        pygame.draw.rect(surface, (0, 0, 0), core_rect)
        jitter = random.randint(-1, 1)
        eye_color = (0, 255, 255) if monster.stun_timer > 0 else (255, 50, 50)
        pygame.draw.line(surface, eye_color, (x - 8*scale, y - 5*scale+jitter), (x - 2*scale, y + 2*scale+jitter), int(2*scale))
        pygame.draw.line(surface, eye_color, (x + 8*scale, y - 5*scale+jitter), (x + 2*scale, y + 2*scale+jitter), int(2*scale))

def draw_vision(surface, player, monster):
    mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    mask.fill((0, 0, 0))
    radius = 170

    # Đèn pin chập chờn rùng rợn khi Quái tới gần
    if monster.active:
        dist = math.hypot(player.x - monster.x, player.y - monster.y)
        if dist < 250:
            if random.random() < 0.25:
                radius = random.randint(60, 120)

    if player.is_exhausted: 
        radius = 80
        mask.fill((20, 0, 0)) 
        
    pygame.draw.circle(mask, (255, 255, 255), (int(player.x), int(player.y)), radius)
    surface.blit(mask, (0, 0), special_flags=pygame.BLEND_MULT)

def draw_blood_vignette(surface, player, monster):
    """Viền màn hình máu cảnh báo nguy hiểm"""
    if not monster.active: return
    dist = math.hypot(player.x - monster.x, player.y - monster.y)
    if dist < 300:
        alpha = int((1.0 - (dist / 300)) * 140)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (255, 0, 0, alpha), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 15)
        surface.blit(vignette, (0, 0))

def draw_radar(surface, player, monster, target_crate, gate):
    if player.is_exhausted: return 

    size = 150
    rect = pygame.Rect(SCREEN_WIDTH - size - 20, SCREEN_HEIGHT - size - 20, size, size)
    pygame.draw.rect(surface, COLOR_RADAR_BG, rect)
    pygame.draw.rect(surface, COLOR_RADAR_LINE, rect, 2)
    angle = (pygame.time.get_ticks() / 10) % 360
    rad = math.radians(angle)
    end_line = (rect.centerx + math.cos(rad) * (size//2), rect.centery + math.sin(rad) * (size//2))
    pygame.draw.line(surface, (0, 100, 0), rect.center, end_line, 2)
    if int(angle) % 180 == 0 and snd_blip: snd_blip.play()
    scale_x = size / SCREEN_WIDTH; scale_y = size / SCREEN_HEIGHT
    if gate.active:
        gx = rect.left + int(gate.x * scale_x)
        gy = rect.top + int(gate.y * scale_y)
        if (pygame.time.get_ticks() // 200) % 2 == 0:
            pygame.draw.circle(surface, COLOR_GATE_GLOW, (gx, gy), 6)
            pygame.draw.circle(surface, COLOR_GATE_GLOW, (gx, gy), 10, 1)
    else:
        ox = rect.left + int(target_crate.x * scale_x)
        oy = rect.top + int(target_crate.y * scale_y)
        c_color = (255, 255, 255) if target_crate.type == "SILVER" else (255, 140, 0)
        pygame.draw.rect(surface, c_color, (ox - 3, oy - 3, 6, 6))
    if monster.active:
        dist = math.hypot(player.x - monster.x, player.y - monster.y)
        if dist < RADAR_DETECTION_RANGE:
            mx = rect.left + int(monster.x * scale_x)
            my = rect.top + int(monster.y * scale_y)
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                pygame.draw.circle(surface, COLOR_RADAR_ENEMY, (mx, my), 4)
    px = rect.left + int(player.x * scale_x)
    py = rect.top + int(player.y * scale_y)
    pygame.draw.circle(surface, (0, 255, 255), (px, py), 3)

def draw_ui(surface, player, current_score, time_left):
    bar_width = 300; bar_height = 25; x = 20; y = 20
    
    # Thanh Hàng Hóa
    pygame.draw.rect(surface, COLOR_BAR_BG, (x, y, bar_width, bar_height))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, bar_width, bar_height), 2)
    if current_score > 0:
        fill_pct = min(1.0, current_score / MAX_ENERGY)
        fill_width = int(fill_pct * bar_width)
        pygame.draw.rect(surface, COLOR_ENERGY, (x + 2, y + 2, fill_width - 4, bar_height - 4))
    txt = font_ui.render(f"CARGO LOAD: {current_score}/{MAX_ENERGY}", True, COLOR_ENERGY)
    surface.blit(txt, (x + bar_width + 10, y))
    
    # Kỹ năng Trạng Thái
    status_y = y + 32
    if player.has_scythe:
        scythe_txt = font_ui.render("[ SHIELD: ACTIVE ]", True, (200, 255, 200))
        surface.blit(scythe_txt, (x, status_y))
        status_y += 22

    dash_str = "READY [SPACE]" if player.dash_cd <= 0 else f"COOLDOWN ({player.dash_cd:.1f}s)"
    dash_col = (0, 255, 255) if player.dash_cd <= 0 else (120, 120, 120)
    dash_txt = font_ui.render(f"CYBER DASH: {dash_str}", True, dash_col)
    surface.blit(dash_txt, (x, status_y))
    status_y += 22

    emp_txt = font_ui.render(f"EMP MINES [E]: {player.emp_charges}", True, (255, 215, 0) if player.emp_charges > 0 else (120, 120, 120))
    surface.blit(emp_txt, (x, status_y))

    # --- ĐỒNG HỒ ĐẾM NGƯỢC ---
    time_color = (0, 255, 255) 
    if time_left <= 15: time_color = (255, 0, 0)
    elif time_left <= 30: time_color = (255, 165, 0)

    timer_box_w, timer_box_h = 220, 80
    box_x = SCREEN_WIDTH - timer_box_w - 20
    box_y = 10
    
    s = pygame.Surface((timer_box_w, timer_box_h))
    s.set_alpha(180)
    s.fill((0, 20, 40))
    surface.blit(s, (box_x, box_y))
    pygame.draw.rect(surface, time_color, (box_x, box_y, timer_box_w, timer_box_h), 2)
    
    lbl = font_ui.render("MISSION TIMER", True, (150, 150, 255))
    lbl_rect = lbl.get_rect(center=(box_x + timer_box_w//2, box_y + 20))
    surface.blit(lbl, lbl_rect)

    minutes = int(time_left) // 60
    seconds = int(time_left) % 60
    time_str = f"{minutes:02}:{seconds:02}"
    
    time_surf = font_digital.render(time_str, True, time_color)
    time_rect = time_surf.get_rect(center=(box_x + timer_box_w//2, box_y + 55))
    surface.blit(time_surf, time_rect)

def wrap_text(surface, text, font, color, max_width, start_x, start_y):
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        w, h = font.size(test_line)
        if w < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    y = start_y
    for line in lines:
        text_surf = font.render(line, True, color)
        rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, y))
        surface.blit(text_surf, rect)
        y += h + 5 

# --- SCENES ---

def cinematic_intro():
    start_ticks = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_ticks < 4000:
        screen.fill((255, 255, 255)) 
        draw_ueh_logo(screen, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)
        
        intro_txt = font_ui.render("FACULTY OF LOGISTICS & INTERNATIONAL TRADE", True, (0, 50, 100))
        intro_rect = intro_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(intro_txt, intro_rect)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
    
    paragraphs = [
        "Alex, a top-notch delivery man, crashes while transporting goods to UEH University, plunging his truck into the mysterious 'Silent Forest.' The accident leaves 10 crucial packages lost in the darkness, forcing him to abandon his vehicle and retrieve them despite the perilous situation.",
        "In the dead of night, a terrifying ancient entity called the 'Void Specter' begins its hunt, poised to devour him. Armed only with a flickering flashlight and handheld radar, Alex painstakingly searches for each package, consumed by fear as the monster draws closer.",
        "Each recovered package brings him closer to hope, but his strength wanes under the relentless pursuit. Just as he reaches the tenth package, a massive surge of energy erupts, activating the 'UEH Guardian Matrix' defense system.",
        "A brilliant golden light descends from above, granting Alex unparalleled orbital power to counterattack the darkness. With a devastating blow, he blasted the Specter monster into dust and dispelled the surrounding darkness.",
    ]

    if bg_music: bg_music.play(-1)
    skip = False
    
    for i, para in enumerate(paragraphs):
        if skip: break
        current_text = ""
        typing_speed = 1 if len(para) > 50 else 3 
        
        for char in para:
            current_text += char
            
            if isinstance(bg_intro_img, pygame.Surface):
                screen.blit(bg_intro_img, (0, 0))
            else:
                screen.fill((5, 10, 15))
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            screen.blit(overlay, (0, 0))
            
            y_offset = 100
            for prev_para in paragraphs[:i]:
                color = (200, 200, 200) 
                wrap_text(screen, prev_para, font_story, color, 800, SCREEN_WIDTH//2, y_offset)
                num_lines = (font_story.size(prev_para)[0] // 800) + 2
                y_offset += num_lines * 30 + 20
            
            color_curr = (0, 255, 255) if "CẢNH BÁO" in para else (255, 255, 255)
            if "UEH" in para: color_curr = (0, 200, 255)
            
            wrap_text(screen, current_text + "_", font_story, color_curr, 800, SCREEN_WIDTH//2, y_offset)
            
            skip_txt = font_ui.render("[SPACE] SKIP BRIEFING", True, (255, 255, 255))
            screen.blit(skip_txt, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 40))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: skip = True
            
            if skip: break
            pygame.time.delay(typing_speed)
        
        pygame.time.delay(2000) 

def show_tutorial():
    lines = [
        "*** LOGISTICS MISSION PROTOCOLS ***",
        "",
        "1. COLLECT 10 PARCELS BEFORE TIME RUNS OUT.",
        "2. TIME LIMIT: 60 SECONDS.",
        "3. DELIVER TO THE EXTRACTION GATE.",
        "",
        "[ CONTROLS & ARSENAL ]",
        "- [WASD]: MOVE  |  [LSHIFT]: SPRINT",
        "- [SPACE]: CYBER DASH (EVADE SPECTER)",
        "- [E]: DROP EMP STASIS MINE (STUNS MONSTER)",
        "- WHITE CRATES: BONUS SHIELD / EMP MINES / +10s TIME.",
        "",
        "PRESS [SPACE] TO START OPERATION"
    ]
    running = True
    while running:
        if isinstance(bg_intro_img, pygame.Surface):
             screen.blit(bg_intro_img, (0, 0))
             overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
             overlay.fill((0,0,0))
             overlay.set_alpha(150)
             screen.blit(overlay, (0,0))
        else:
             screen.fill((10, 10, 20))

        y = 100
        for line in lines:
            col = (0, 255, 255)
            if "CONTROLS" in line: col = (255, 215, 0)
            if "WHITE" in line: col = (255, 255, 255)
            if "TIME LIMIT" in line: col = (255, 100, 100)
            txt = font_ui.render(line, True, col)
            rect = txt.get_rect(center=(SCREEN_WIDTH//2, y))
            screen.blit(txt, rect)
            y += 35
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: running = False
        clock.tick(60)

def trigger_orbital_strike_victory(screen, player, monster, gate):
    if snd_orbital_charge: snd_orbital_charge.play()
    start_time = pygame.time.get_ticks()
    duration = 6000 
    impact_time = 1800 
    has_boomed = False
    while pygame.time.get_ticks() - start_time < duration:
        current_time = pygame.time.get_ticks() - start_time
        screen.fill(COLOR_BG)
        shake_intensity = 2 if current_time < impact_time else 25
        shake_x = random.randint(-shake_intensity, shake_intensity)
        shake_y = random.randint(-shake_intensity, shake_intensity)
        draw_delivery_gate_advanced(screen, gate)
        draw_player_avatar(screen, player)

        if current_time < 1500:
            draw_spectral_monster(screen, monster)
            angle = (current_time / 5) % 360
            rad = math.radians(angle)
            reticle_r = 120 - (current_time / 20)
            pygame.draw.arc(screen, COLOR_WARNING_RED, (monster.x - reticle_r, monster.y - reticle_r, reticle_r*2, reticle_r*2), rad, rad + 2, 2)
            pygame.draw.arc(screen, COLOR_WARNING_RED, (monster.x - reticle_r, monster.y - reticle_r, reticle_r*2, reticle_r*2), rad + 3.14, rad + 5.14, 2)
            if (current_time // 100) % 2 == 0:
                 txt = font_ui.render("ORBITAL LOCK: CONFIRMED", True, COLOR_WARNING_RED)
                 screen.blit(txt, (monster.x - 100, monster.y - 150))
        elif current_time < impact_time:
            draw_spectral_monster(screen, monster)
            for _ in range(10):
                angle = random.uniform(0, 6.28)
                dist = random.randint(50, 200)
                sx = monster.x + math.cos(angle) * dist
                sy = monster.y + math.sin(angle) * dist
                pygame.draw.line(screen, (255, 255, 255), (sx, sy), (monster.x, monster.y), 2)
        elif current_time < 4500:
            if not has_boomed:
                if snd_orbital_boom: snd_orbital_boom.play()
                has_boomed = True
                screen.fill((255, 255, 255)) 
            draw_spectral_monster(screen, monster, scale=1.5, is_dying=True)
            beam_w = random.randint(100, 150)
            pygame.draw.line(screen, (200, 255, 255), (monster.x, 0), (monster.x, monster.y + 50), beam_w)
            pygame.draw.line(screen, COLOR_ORBITAL_BEAM, (monster.x, 0), (monster.x, monster.y + 50), beam_w + 50)
            wave_r = (current_time - impact_time) * 1.5
            pygame.draw.circle(screen, COLOR_ORBITAL_BEAM, (monster.x, monster.y), int(wave_r), 15)
            pygame.draw.circle(screen, (255, 255, 255), (monster.x, monster.y), int(wave_r * 0.7), 5)
        else:
            for _ in range(60):
                px = monster.x + random.randint(-100, 100)
                py = monster.y + random.randint(-50, 50) - (current_time - 4500) * 0.2
                pygame.draw.circle(screen, (100, 100, 100), (px, py), random.randint(1, 4))
        pygame.display.flip()
        clock.tick(0)

def trigger_enhanced_death(screen, message="SYSTEM TERMINATED"):
    if snd_scream: snd_scream.play()
    if snd_glitch: snd_glitch.play()
    
    dummy_monster = Monster()
    dummy_monster.x = SCREEN_WIDTH // 2
    dummy_monster.y = SCREEN_HEIGHT // 2

    end = pygame.time.get_ticks() + 1800
    while pygame.time.get_ticks() < end:
        if (pygame.time.get_ticks() // 50) % 2 == 0:
            screen.fill((255, 255, 255)) 
        else:
            screen.fill((0, 0, 0)) 
        
        shake_x = random.randint(-30, 30)
        shake_y = random.randint(-30, 30)
        dummy_monster.x = SCREEN_WIDTH // 2 + shake_x
        dummy_monster.y = SCREEN_HEIGHT // 2 + shake_y
        
        draw_spectral_monster(screen, dummy_monster, scale=9.0)
        
        for _ in range(20):
            glitch_y = random.randint(0, SCREEN_HEIGHT)
            glitch_h = random.randint(5, 50)
            offset = random.randint(-30, 30)
            rect = pygame.Rect(0, glitch_y, SCREEN_WIDTH, glitch_h)
            try:
                sub = screen.subsurface(rect).copy()
                screen.blit(sub, (offset, glitch_y))
            except: pass
            
            if random.random() < 0.4:
                pygame.draw.line(screen, (random.randint(0,255), 0, 0), (0, glitch_y), (SCREEN_WIDTH, glitch_y), 3)
        
        shadow_surf = font_glitch.render(message, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH//2 + 5, SCREEN_HEIGHT//2 + 5))
        screen.blit(shadow_surf, shadow_rect)

        msg = font_glitch.render(message, True, COLOR_WARNING_RED)
        rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(msg, rect)
            
        pygame.display.flip()
        clock.tick(60)

def show_game_over(win, reason="SHIPMENT LOST"):
    while True:
        if win:
            if isinstance(bg_gameover_img, pygame.Surface):
                screen.blit(bg_gameover_img, (0, 0))
            else:
                screen.fill((10, 20, 10))

            txt = font_victory.render("DELIVERY SUCCESSFUL!", True, COLOR_VICTORY_TEXT)
            rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(txt, rect)
            sub = font_ui.render("SPECTER OBLITERATED. UEH LOGISTICS: MISSION ACCOMPLISHED.", True, (200, 200, 200))
            sub_rect = sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            screen.blit(sub, sub_rect)
        else:
            screen.fill((0, 0, 0))
            for i in range(25):
                err_code = f"ERR_0x{random.randint(1000,9999)}: CRITICAL_FAILURE_SECTOR_{random.randint(0,99)}"
                code_txt = font_ui.render(err_code, True, (0, 80, 0))
                screen.blit(code_txt, (10, i * 30))

            txt = font_scary.render(reason, True, (255, 0, 0))
            rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(txt, rect)
        
        retry = font_ui.render("[R] NEW CONTRACT", True, (200, 200, 200))
        retry_rect = retry.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        screen.blit(retry, retry_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: main()

# --- MAIN ---
def main():
    player = Player()
    monster = Monster()
    gate = DeliveryGate()
    score = 0
    time_left = GAME_DURATION
    
    emp_traps = []
    fogs = [FogParticle() for _ in range(12)]
    heartbeat_timer = 0
    
    last_was_silver = False
    current_crate = LootCrate(score, force_normal=last_was_silver)
    
    cinematic_intro()
    show_tutorial()
    
    running = True
    monster_triggered = False
    popup = {"text": "", "timer": 0, "color": (255, 255, 255)}
    
    timeout_triggered = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        screen.fill(COLOR_BG)
        
        # Cập nhật & Vẽ sương mù
        for fog in fogs:
            fog.update(dt)
            fog.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                # Đặt Mìn EMP (Phím E)
                if event.key == pygame.K_e and player.emp_charges > 0:
                    player.emp_charges -= 1
                    emp_traps.append(EmpTrap(player.x, player.y))
                    if snd_emp: snd_emp.play()
                    popup = {"text": "EMP STASIS MINE DEPLOYED!", "timer": 90, "color": (0, 255, 255)}

        if not gate.active and not timeout_triggered: 
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                if not timeout_triggered:
                    timeout_triggered = True
                    gate.is_locked = True
                    monster.active = True
                    monster.frenzy_mode = True 
                    player.is_exhausted = True 
                    if snd_gate_alarm: snd_gate_alarm.play()
                    popup = {"text": "CONTRACT EXPIRED! GATES LOCKED!", "timer": 200, "color": (255, 0, 0)}

        if score >= MAX_ENERGY and not gate.active and not timeout_triggered:
            gate.active = True
            if snd_gate_alarm: snd_gate_alarm.play()
            popup = {"text": "CARGO FULL! DELIVER TO THE GATE!", "timer": 180, "color": COLOR_GATE_GLOW}
            current_crate.x = -1000
        
        if gate.active and not timeout_triggered:
            if math.hypot(player.x - gate.x, player.y - gate.y) < 60:
                trigger_orbital_strike_victory(screen, player, monster, gate)
                show_game_over(win=True)
                return

        # Thu thập thùng hàng
        if not gate.active and math.hypot(player.x - current_crate.x, player.y - current_crate.y) < 40 and not timeout_triggered:
            if current_crate.type == "SILVER":
                last_was_silver = True 
                if snd_equip: snd_equip.play()
                
                rand_val = random.random()
                if current_crate.has_time_bonus:
                    time_left += 10
                    if snd_time_bonus: snd_time_bonus.play()
                    popup = {"text": "EXTENSION GRANTED: +10 SECONDS!", "timer": 120, "color": (255, 215, 0)}
                elif rand_val < 0.35:
                    score += 2
                    popup = {"text": "BONUS CARGO: +2 UNITS!", "timer": 120, "color": COLOR_ENERGY}
                elif rand_val < 0.7:
                    player.has_scythe = True
                    popup = {"text": "SHIELD MODULE EQUIPPED!", "timer": 120, "color": COLOR_SILVER_GLOW}
                else:
                    player.emp_charges += 1
                    popup = {"text": "SUPPLY FOUND: +1 EMP MINE!", "timer": 120, "color": (0, 255, 255)}
                
                if score >= TRIGGER_COUNT and not monster.active:
                    monster.active = True; monster_triggered = True; snd_alert.play()

            else:
                last_was_silver = False 
                if current_crate.is_empty:
                    if snd_open_bad: snd_open_bad.play()
                    popup = {"text": "EMPTY CONTAINER...", "timer": 60, "color": (150, 150, 150)}
                else:
                    score += 1
                    if snd_open_good: snd_open_good.play()
                    popup = {"text": "CARGO SECURED", "timer": 60, "color": COLOR_ENERGY}
                    if score >= TRIGGER_COUNT and not monster.active:
                        monster.active = True; monster_triggered = True; snd_alert.play()

            if score >= 5: monster.speed = MONSTER_BASE_SPEED + (score - 4) * 15
            if score < MAX_ENERGY: 
                current_crate = LootCrate(score, force_normal=last_was_silver)

        player.move(pygame.key.get_pressed(), dt)
        monster.hunt(player.x, player.y, dt)

        # Tiếng Nhịp Tim Thót Tim Khi Quái Đến Gần
        if monster.active:
            dist = math.hypot(player.x - monster.x, player.y - monster.y)
            if dist < 280:
                heartbeat_timer += dt
                rate = 0.3 if dist < 120 else 0.6
                if heartbeat_timer >= rate:
                    if snd_heartbeat: snd_heartbeat.play()
                    heartbeat_timer = 0

        # Kiểm tra bẫy Mìn EMP kích hoạt
        for trap in emp_traps[:]:
            trap.draw(screen)
            if trap.active and monster.active and math.hypot(monster.x - trap.x, monster.y - trap.y) < 45:
                trap.active = False
                emp_traps.remove(trap)
                monster.stun_timer = 3.5 # Tê liệt 3.5 giây
                if snd_emp: snd_emp.play()
                popup = {"text": "SPECTER STUNNED BY EMP!", "timer": 100, "color": (0, 255, 255)}

        # Kiểm tra va chạm Quái vật
        if monster.active and math.hypot(player.x - monster.x, player.y - monster.y) < 30:
            if player.has_scythe and not timeout_triggered:
                player.has_scythe = False
                if snd_shield_break: snd_shield_break.play()
                popup = {"text": "SHIELD BROKEN! SPECTER REPELLED!", "timer": 90, "color": (255, 50, 50)}
                dx, dy = monster.x - player.x, monster.y - player.y
                dist = math.hypot(dx, dy)
                if dist == 0: dist = 1
                monster.x += (dx/dist) * 350; monster.y += (dy/dist) * 350
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); flash.fill((200, 255, 255)); flash.set_alpha(150)
                screen.blit(flash, (0,0)); pygame.display.flip()
            else:
                reason = "SHIPMENT LOST"
                if timeout_triggered:
                    trigger_enhanced_death(screen, "TIMEOUT_FAILURE")
                    reason = "CONTRACT EXPIRED"
                else:
                    trigger_enhanced_death(screen)
                show_game_over(win=False, reason=reason)
                return
        
        if not gate.active: draw_scifi_crate(screen, current_crate.x, current_crate.y, current_crate.type, current_crate.has_time_bonus)
        draw_delivery_gate_advanced(screen, gate)
        if monster.active: draw_spectral_monster(screen, monster)
        draw_player_avatar(screen, player)
        draw_vision(screen, player, monster)
        draw_blood_vignette(screen, player, monster)
        
        if popup["timer"] > 0:
            surf = font_popup.render(popup["text"], True, popup["color"])
            rect = surf.get_rect(center=(player.x, player.y - 70))
            screen.blit(surf, rect)
            popup["timer"] -= 1
            
        draw_ui(screen, player, score, time_left)
        draw_radar(screen, player, monster, current_crate, gate)
        
        if monster_triggered and not timeout_triggered:
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                txt = font_ui.render("!!! SPECTER APPROACHING !!!", True, (255, 0, 0))
                rect = txt.get_rect(center=(SCREEN_WIDTH//2, 100))
                screen.blit(txt, rect)
            if pygame.time.get_ticks() % 3000 < 50: monster_triggered = False
        
        if timeout_triggered:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                 txt = font_ui.render("!!! CRITICAL FAILURE: GATE CLOSED !!!", True, (255, 0, 0))
                 rect = txt.get_rect(center=(SCREEN_WIDTH//2, 100))
                 screen.blit(txt, rect)

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()