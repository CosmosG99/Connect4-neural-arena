import pygame
import random
import math
import time
from config import config, BASE_WIDTH, BASE_HEIGHT, ROWS, COLS, EMPTY, PLAYER, AI_AGENT, MODE_H_VS_AI, MODE_AI_VS_AI, MODE_H_VS_H
from audio import audio_sys

pygame.init()

# Fonts cache based on size
_font_cache = {}

def get_font(name, size, bold=False):
    size = config.s(size)
    key = f"{name}_{size}_{bold}"
    if key not in _font_cache:
        try:
            _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
        except:
            _font_cache[key] = pygame.font.Font(None, size)
            if bold:
                _font_cache[key].set_bold(True)
    return _font_cache[key]

def draw_text(surface, text, font, color, x, y, center=True, align_right=False):
    """Robust text rendering with alignment support"""
    if text is None: text = ""
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    elif align_right:
        text_rect.midright = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_elegant_text(surface, text, font, color, x, y, shadow_offset=2, center=True):
    # Pure clean drop shadow for max contrast (no blur/glow)
    shadow_offset = max(1, config.s(shadow_offset))
    shadow_surf = font.render(text, True, (0, 0, 0))
    # Full opacity shadow for maximum contrast
    shadow_rect = shadow_surf.get_rect()
    if center:
        shadow_rect.center = (x + shadow_offset, y + shadow_offset)
    else:
        shadow_rect.topleft = (x + shadow_offset, y + shadow_offset)
    surface.blit(shadow_surf, shadow_rect)
            
    # Crisp main text
    draw_text(surface, text, font, color, x, y, center)

def draw_gradient_text(surface, text, font, color1, color2, x, y, glow_color=None, center=True):
    """Draws text with a vertical gradient and optional outer glow"""
    text_surf = font.render(text, True, (255, 255, 255))
    w, h = text_surf.get_size()
    
    # Create gradient overlay
    gradient_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        ratio = i / h
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(gradient_surf, (r, g, b, 255), (0, i), (w, i))
        
    # Apply gradient to text using BLEND_RGBA_MULT
    # Ensure final_text has alpha channel
    final_text = pygame.Surface((w, h), pygame.SRCALPHA)
    final_text.blit(text_surf, (0, 0))
    final_text.blit(gradient_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    rect = final_text.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
        
    # Draw glow if requested
    if glow_color:
        for i in range(1, 5):
            alpha = int(60 / i)
            glow_surf = font.render(text, True, (*glow_color, alpha))
            g_rect = glow_surf.get_rect(center=rect.center)
            surface.blit(glow_surf, g_rect)
            
    surface.blit(final_text, rect)
    return rect

def draw_spaced_text(surface, text, font, color, x, y, spacing=5, alpha=255, center=True):
    """Draws text with custom letter spacing and alpha"""
    chars = [font.render(c, True, color) for c in text]
    total_w = sum(c.get_width() for c in chars) + (len(text) - 1) * spacing
    
    curr_x = x - total_w // 2 if center else x
    for c in chars:
        if alpha < 255:
            c.set_alpha(alpha)
        surface.blit(c, (curr_x, y - c.get_height() // 2 if center else y))
        curr_x += c.get_width() + spacing
    return pygame.Rect(x - total_w // 2 if center else x, y - chars[0].get_height() // 2 if center else y, total_w, chars[0].get_height())

class GlassPanel:
    def __init__(self, x, y, width, height, alpha=245):
        self.rect = pygame.Rect(x, y, width, height)
        self.alpha = alpha

    def draw(self, surface):
        rect = pygame.Rect(config.s(self.rect.x), config.s(self.rect.y), config.s(self.rect.width), config.s(self.rect.height))
        
        # 1. Outer Deep Shadow
        shadow_rect = rect.copy()
        shadow_rect.y += config.s(8)
        pygame.draw.rect(surface, (0, 0, 0, 180), shadow_rect, border_radius=config.s(14))

        # 2. Main Background (Dynamic Panel BG from config)
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_color = config.PANEL_BG
        s.fill(panel_color) 
        
        # Matte sci-fi scanline texture
        for i in range(0, rect.height, config.s(4)):
            pygame.draw.line(s, (0, 0, 0, 35), (0, i), (rect.width, i), config.s(1))
            
        surface.blit(s, (rect.x, rect.y))
        
        # 3. Layered Premium Gold Border (Thin & Sharp)
        glow_steps = max(1, config.s(10))
        for i in range(glow_steps):
            a = int(30 * (1 - i / glow_steps))
            pygame.draw.rect(surface, (*config.THEME_ACCENT_1, a), rect.inflate(config.s(i*2), config.s(i*2)), max(1, config.s(1)), border_radius=config.s(14+i))

        pygame.draw.rect(surface, config.THEME_ACCENT_1, rect, max(1, config.s(3)), border_radius=config.s(14))

class Button:
    def __init__(self, x, y, width, height, text, color_key, font_size, action=None, value=None, is_toggle=False):
        self.logical_rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(config.s(x), config.s(y), config.s(width), config.s(height))
        self.text = text
        self.color_key = color_key # Key for config color (e.g. 'PLAYER1_COLOR')
        self.font_size = font_size
        self.action = action
        self.value = value
        self.is_toggle = is_toggle
        self.active = False
        self.is_hovered = False
        self.hover_progress = 0.0
        self.click_progress = 0.0
        self.shine_timer = random.uniform(0, 5.0)
        self.icon_type = None 

    def draw(self, surface):
        self.rect = pygame.Rect(config.s(self.logical_rect.x), config.s(self.logical_rect.y), 
                                config.s(self.logical_rect.width), config.s(self.logical_rect.height))
        
        if self.is_hovered:
            self.hover_progress = min(1.0, self.hover_progress + 0.1)
        else:
            self.hover_progress = max(0.0, self.hover_progress - 0.1)
            
        self.click_progress = max(0.0, self.click_progress - 0.15)
        self.shine_timer += 0.016
            
        font = get_font("segoe ui", self.font_size, bold=True)
        
        # Click Compression and Hover Scale
        scale_offset = int((self.hover_progress * 4 - self.click_progress * 6) * config.scale_factor)
        draw_rect = self.rect.inflate(scale_offset, scale_offset)
        
        # Dynamic Color Retrieval
        base_color = getattr(config, self.color_key, config.THEME_ACCENT_1)
        
        # 1. Shadow Shift on hover/click
        shadow_rect = draw_rect.copy()
        shadow_y = 6 - (self.click_progress * 4)
        shadow_rect.y += config.s(shadow_y)
        pygame.draw.rect(surface, (0, 0, 0, 180), shadow_rect, border_radius=config.s(10))
            
        # 2. Base Button Body
        if self.is_toggle and self.active:
            bg_base = base_color
        else:
            bg_base = (5, 8, 20) # Always dark midnight
            
        if self.hover_progress > 0 and not (self.is_toggle and self.active):
            bg_base = tuple(min(255, c + int(20 * self.hover_progress)) for c in bg_base)
            
        # Main Rounded Rect
        pygame.draw.rect(surface, bg_base, draw_rect, border_radius=config.s(10))
        
        # Add Glossy Radial Highlight
        gloss_surf = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
        # Upper gloss
        for i in range(draw_rect.height // 2):
            a = int(60 * (1 - i / (draw_rect.height // 2)))
            pygame.draw.line(gloss_surf, (255, 255, 255, a), (config.s(5), i), (draw_rect.width - config.s(5), i))
        surface.blit(gloss_surf, draw_rect.topleft)
        
        # 3. Soft Golden Glow on Hover
        if self.hover_progress > 0:
            glow_surf = pygame.Surface(draw_rect.inflate(config.s(15), config.s(15)).size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*config.THEME_ACCENT_1, int(45 * self.hover_progress)), glow_surf.get_rect(), border_radius=config.s(12), width=config.s(2))
            surface.blit(glow_surf, draw_rect.inflate(config.s(15), config.s(15)).topleft)
            
        # 4. Premium Structural Gold Border
        if self.is_toggle and self.active:
            # Pulsing Glow for Active State
            pulse = abs(math.sin(time.time() * 6)) * 100
            border_color = tuple(min(255, c + int(pulse)) for c in base_color)
            border_thickness = max(1, config.s(4))
        else:
            # Sharp Gold Outline
            border_color = config.THEME_ACCENT_1 if self.hover_progress > 0 else (*config.THEME_ACCENT_1, 120)
            border_thickness = max(1, config.s(2))
            
        pygame.draw.rect(surface, border_color, draw_rect, border_thickness, border_radius=config.s(10))
        # Subtle internal depth shadow
        pygame.draw.rect(surface, (0, 0, 0, 80), draw_rect.inflate(config.s(-2), config.s(-2)), max(1, config.s(1)), border_radius=config.s(9))
        
        # Draw Icons and Text
        self._draw_content(surface, draw_rect, font)

    def _draw_content(self, surface, rect, font):
        text_surf = font.render(self.text, True, config.WHITE)
        text_rect = text_surf.get_rect()
        
        if self.icon_type:
            # 1. Calculate precise dimensions for horizontal centering
            icon_w = config.s(32) # Standard icon size
            icon_gap = config.s(8) # Gap between icons in a group
            group_gap = config.s(20) # Gap between icon group and text
            
            icon_group_w = (icon_w * 2) + icon_gap
            total_w = icon_group_w + group_gap + text_rect.width
            
            # Start position for the group
            start_x = rect.centerx - total_w // 2
            
            # 2. Draw Icon Group (Vertically Centered)
            group_rect = pygame.Rect(start_x, rect.centery - icon_w // 2, icon_group_w, icon_w)
            self._draw_icon_group(surface, group_rect, icon_w, icon_gap)
            
            # 3. Draw Text (Vertically Centered)
            text_x = start_x + icon_group_w + group_gap + text_rect.width // 2
            draw_elegant_text(surface, self.text, font, config.WHITE, text_x, rect.centery, 2)
        else:
            draw_elegant_text(surface, self.text, font, config.WHITE, rect.centerx, rect.centery, 2)

    def _draw_icon_group(self, surface, rect, icon_w, gap):
        """Draws the pair of icons with perfect horizontal alignment"""
        color = (250, 240, 210) # Soft Gold/Cream
        
        x1 = rect.x
        x2 = rect.x + icon_w + gap
        y = rect.y
        
        if self.icon_type == 'human_ai':
            self._draw_human(surface, x1, y, icon_w, color)
            self._draw_robot(surface, x2, y, icon_w, color)
        elif self.icon_type == 'ai_ai':
            self._draw_robot(surface, x1, y, icon_w, color)
            self._draw_robot(surface, x2, y, icon_w, color)
        elif self.icon_type == 'human_human':
            self._draw_human(surface, x1, y, icon_w, color)
            self._draw_human(surface, x2, y, icon_w, color)

    def _draw_human(self, surface, x, y, size, color):
        # Perfectly centered within its allocated square
        cx, cy = x + size // 2, y + size // 2
        
        # Head
        pygame.draw.circle(surface, color, (cx, cy - size // 6), size // 4)
        # Body
        body_w = size // 2
        body_h = size // 3
        body_rect = pygame.Rect(cx - body_w // 2, cy + size // 12, body_w, body_h)
        pygame.draw.rect(surface, color, body_rect, border_top_left_radius=size // 6, border_top_right_radius=size // 6)

    def _draw_robot(self, surface, x, y, size, color):
        # Perfectly centered within its allocated square
        cx, cy = x + size // 2, y + size // 2
        
        # Head/Body
        bot_w = 2 * size // 3
        bot_h = size // 2
        bot_rect = pygame.Rect(cx - bot_w // 2, cy - bot_h // 3, bot_w, bot_h)
        pygame.draw.rect(surface, color, bot_rect, border_radius=size // 10)
        # Eyes
        eye_r = size // 15
        pygame.draw.circle(surface, config.BG_COLOR, (bot_rect.x + bot_rect.width // 4, bot_rect.centery), eye_r)
        pygame.draw.circle(surface, config.BG_COLOR, (bot_rect.right - bot_rect.width // 4, bot_rect.centery), eye_r)
        # Antennas
        pygame.draw.line(surface, color, (cx, bot_rect.y), (cx, bot_rect.y - size // 6), config.s(2))
        pygame.draw.circle(surface, color, (cx, bot_rect.y - size // 6), size // 20)

    def check_hover(self, pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(pos)
        if self.is_hovered and not was_hovered:
            audio_sys.play_sfx('hover')
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                audio_sys.play_sfx('click')
                self.click_progress = 1.0
                if self.is_toggle:
                    self.active = not self.active
                if self.action:
                    return self.value if self.value is not None else True
        return False

class AmbientParticle:
    def __init__(self, theme='default'):
        self.x = random.randint(0, BASE_WIDTH)
        self.y = random.randint(0, BASE_HEIGHT)
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(-0.2, 0.05)
        self.life = random.randint(200, 500)
        self.max_life = self.life
        if theme == 'intro':
            self.color = random.choice([config.WHITE, config.THEME_HIGHLIGHT, (255, 240, 180)]) # White and Warm Golden
            self.size = random.uniform(1.2, 3.2) # Varied tiny stars
        else:
            self.color = random.choice(config.PARTICLE_COLORS + [config.THEME_HIGHLIGHT])
            self.size = random.uniform(2, 4.5) 
        self.parallax = random.uniform(0.1, 0.3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life <= 0:
            self.__init__(theme='intro' if self.size < 3 else 'default')

    def draw(self, surface):
        # Sharper twinkling stars
        pulse = abs(math.sin(time.time() * 3 + self.x)) 
        alpha = int(min(1.0, self.life / 60.0) * min(1.0, (self.max_life - self.life) / 60.0) * (100 + pulse * 50))
        if alpha > 0:
            sx, sy = config.s((self.x, self.y))
            size = max(1, config.s(self.size))
            # Draw core
            pygame.draw.circle(surface, (*self.color, alpha), (sx, sy), size)
            # Sharper subtle glow
            if alpha > 40:
                glow_size = size * 2.5
                glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha // 4), (glow_size, glow_size), glow_size)
                surface.blit(glow_surf, (sx - glow_size, sy - glow_size))

class ParticleSystem:
    def __init__(self, count):
        self.particles = [AmbientParticle() for _ in range(count)]

    def update_and_draw(self, surface):
        for p in self.particles:
            p.update()
            p.draw(surface)

class Cloud:
    def __init__(self, layer):
        self.layer = layer # 0: Deep (slow), 1: Mid, 2: Near (fast)
        self.reset(start_random=True)
        
    def reset(self, start_random=False):
        # Professional atmospheric clouds (elongated & feathered)
        self.width = random.randint(400, 800) 
        self.height = random.randint(60, 140)
        
        if start_random:
            self.x = random.randint(-self.width, BASE_WIDTH)
        else:
            self.x = -self.width - random.randint(200, 800)
            
        self.y = random.randint(0, BASE_HEIGHT // 2 + 300)
        # Medium pace, smooth cinematic motion (Autonomous L to R)
        self.speed = (self.layer + 1) * 0.65 + random.uniform(-0.1, 0.1)
        # Increased visibility/opacity
        self.alpha = 60 + self.layer * 25
        self.parallax = 0 # Explicitly remove parallax
        
        self.surf = pygame.Surface(config.s((self.width * 1.5, self.height * 2.5)), pygame.SRCALPHA)
        
        # Slightly brighter atmospheric colors for better visibility
        colors = [(160, 120, 220), (120, 80, 180), (80, 50, 140)]
        
        segments = random.randint(12, 20)
        for _ in range(segments):
            # Elongated base segments
            bx = random.randint(0, self.width)
            by = random.randint(self.height // 4, self.height // 1.2)
            # More elongated width for 'nebula' look
            br_w = random.randint(150, 350)
            br_h = random.randint(40, 80)
            
            color = random.choice(colors)
            
            # Feathered edges using many low-alpha concentric ellipses
            for i in range(10): 
                ratio = (10 - i) / 10
                curr_w = int(br_w * ratio)
                curr_h = int(br_h * ratio)
                curr_a = int(self.alpha * (0.05 + 0.08 * i)) # Slightly higher alpha for visibility
                
                rect = pygame.Rect(bx - curr_w, by - curr_h, curr_w * 2, curr_h * 2)
                pygame.draw.ellipse(self.surf, (*color, curr_a), config.s(rect))
                
                # Add soft highlight on top of nebula for definition
                if i == 9:
                    pygame.draw.ellipse(self.surf, (255, 255, 255, int(self.alpha * 0.2)), config.s(rect.inflate(-2, -2)))
                
        # Optional: Add small puffy "wisps" on top (Brighter for cinematic feel)
        for _ in range(5):
            wx = random.randint(self.width // 4, 3 * self.width // 4)
            wy = random.randint(0, self.height // 3)
            wr = random.randint(30, 60)
            for i in range(8): # More glow layers
                ratio = (8 - i) / 8
                curr_r = int(wr * ratio)
                curr_a = int(self.alpha * (0.05 + 0.05 * i))
                pygame.draw.circle(self.surf, (255, 255, 255, curr_a), config.s((wx, wy)), config.s(curr_r))

    def update(self):
        self.x += self.speed # Continuous medium-pace looping motion
        if self.x > BASE_WIDTH + 200:
            self.reset()

    def draw(self, surface):
        surface.blit(self.surf, config.s((self.x, self.y)))

class CloudSystem:
    def __init__(self, count=12):
        self.clouds = [Cloud(i % 3) for i in range(count)]

    def update_and_draw(self, surface):
        for c in self.clouds:
            c.update()
            c.draw(surface)

class ConstellationNode:
    def __init__(self):
        self.x = random.randint(0, BASE_WIDTH)
        self.y = random.randint(0, BASE_HEIGHT)
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.2, 0.2)
        self.size = random.uniform(1, 4.5) # Varied sizes
        self.color = random.choice([config.WHITE, (220, 200, 255), config.THEME_HIGHLIGHT])
        self.pulse = random.uniform(0, math.pi * 2)
        self.twinkle_speed = random.uniform(0.02, 0.08)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > BASE_WIDTH: self.vx *= -1
        if self.y < 0 or self.y > BASE_HEIGHT: self.vy *= -1
        self.pulse += self.twinkle_speed

    def draw(self, surface, alpha=255, scroll_x=0):
        sx, sy = config.s((self.x + scroll_x * 0.1, self.y))
        pulse_val = (math.sin(self.pulse) + 1) / 2
        current_alpha = max(0, min(255, int(alpha * (0.3 + 0.7 * pulse_val))))
        
        if current_alpha <= 0: return
        
        size = config.s(self.size)
        glow_s = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*self.color, current_alpha // 3), (size*2, size*2), size*2)
        surface.blit(glow_s, (sx - size*2, sy - size*2))
        
        pygame.draw.circle(surface, (*self.color, current_alpha), (sx, sy), config.s(self.size / 2))

class ShootingStar:
    def __init__(self):
        self.reset()

    def reset(self):
        self.active = False
        self.timer = random.randint(30, 200) # Faster appearance
        self.x = random.randint(0, BASE_WIDTH)
        self.y = random.randint(0, BASE_HEIGHT // 2)
        self.vx = random.uniform(12, 25) # Faster
        self.vy = random.uniform(3, 8)
        self.life = 0
        self.max_life = random.randint(30, 60) # Longer trails

    def update(self):
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = True
        else:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.99 # Slight deceleration for elegance
            self.life += 1
            if self.life >= self.max_life:
                self.reset()
    def draw(self, surface, alpha=255):
        if self.active:
            # Multi-layered smooth streak trail (Higher density to avoid dots)
            for i in range(30): 
                segment_alpha = max(0, min(255, int(alpha * (1 - i/30) * (1 - self.life/self.max_life) * 0.8)))
                if segment_alpha <= 0: continue
                # Very tight spacing for streak effect
                sx, sy = config.s((self.x - self.vx * i * 0.15, self.y - self.vy * i * 0.15))
                size = max(1, config.s(2.5 * (1 - i/30)))
                pygame.draw.circle(surface, (*config.WHITE, segment_alpha), (sx, sy), size)
            
            # Head glow
            head_sx, head_sy = config.s((self.x, self.y))
            head_alpha = max(0, min(255, int(alpha * (1 - self.life/self.max_life))))
            pygame.draw.circle(surface, (*config.THEME_HIGHLIGHT, head_alpha // 2), (head_sx, head_sy), config.s(5))
            pygame.draw.circle(surface, (*config.WHITE, head_alpha), (head_sx, head_sy), config.s(1.5))


class ConstellationSystem:
    def __init__(self, node_count=30): # Reduced overcrowding
        self.nodes = [ConstellationNode() for _ in range(node_count)]
        self.stars = [ShootingStar() for _ in range(3)] # 2-3 maximum
        self.connection_dist = 220

    def update_and_draw(self, surface, alpha=255, scroll_x=0):
        for s in self.stars:
            s.update()
            s.draw(surface, alpha)
            
        for i, n1 in enumerate(self.nodes):
            n1.update()
            n1.draw(surface, alpha, scroll_x)
            for j in range(i + 1, len(self.nodes)):
                n2 = self.nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < self.connection_dist:
                    line_alpha = int(alpha * (1 - dist / self.connection_dist) * 0.4)
                    p1 = config.s((n1.x, n1.y))
                    p2 = config.s((n2.x, n2.y))
                    pygame.draw.line(surface, (*config.THEME_ACCENT_1, line_alpha), p1, p2, config.s(1))

class AI_Panel:
    def __init__(self, logical_x, logical_y, logical_width, logical_height):
        self.lx = logical_x
        self.ly = logical_y
        self.lw = logical_width
        self.lh = logical_height
        # Move eval bar inside the panel on the far left
        self.eval_bar = EvalBar(logical_x + 10, logical_y + 110, 15, 330)
        
    def draw(self, surface, stats1, stats2, current_turn, mode, match_telemetry):
        rect = pygame.Rect(config.s(self.lx), config.s(self.ly), config.s(self.lw), config.s(self.lh))
        
        shadow_rect = rect.copy()
        shadow_rect.y += config.s(8)
        pygame.draw.rect(surface, (0, 0, 0, 180), shadow_rect, border_radius=config.s(14))

        pygame.draw.rect(surface, config.PANEL_BG, rect, border_radius=config.s(14))
        
        pygame.draw.rect(surface, (*config.THEME_ACCENT_1, 180), rect, config.s(4), border_radius=config.s(14))
        pygame.draw.rect(surface, (0, 0, 0, 180), rect.inflate(config.s(6), config.s(6)), config.s(2), border_radius=config.s(16))
        
        font_header = get_font("segoe ui", 32, bold=True)
        font_sub = get_font("segoe ui", 24, bold=True)
        font_body = get_font("segoe ui", 20)
        
        draw_elegant_text(surface, "TELEMETRY", font_header, config.WHITE, rect.centerx, rect.y + config.s(45))
        pygame.draw.line(surface, (*config.THEME_ACCENT_1, 150), (rect.x + config.s(30), rect.y + config.s(85)), (rect.right - config.s(30), rect.y + config.s(85)), config.s(3))

        y_offset = rect.y + config.s(110)
        
        # 1. Evaluation Bar (Left Section)
        self.eval_bar.draw(surface)
        
        if stats1:
            self.draw_stats(surface, stats1, "P1 AI (RED)", config.PLAYER1_COLOR, rect.x + config.s(45), y_offset, current_turn == 0, font_sub, font_body)
        elif mode == MODE_H_VS_H or mode == MODE_H_VS_AI:
            self.draw_human_telemetry(surface, "PLAYER 1 (RED)", config.PLAYER1_COLOR, rect.x + config.s(45), y_offset, current_turn == 0, font_sub, font_body, match_telemetry)

        y_offset += config.s(250) # Reduced from 280 to prevent overlap
        
        if stats2:
            self.draw_stats(surface, stats2, "P2 AI (YELLOW)", config.PLAYER2_COLOR, rect.x + config.s(45), y_offset, current_turn == 1, font_sub, font_body)
        elif mode == MODE_H_VS_H:
            self.draw_human_telemetry(surface, "PLAYER 2 (YELLOW)", config.PLAYER2_COLOR, rect.x + config.s(45), y_offset, current_turn == 1, font_sub, font_body, match_telemetry)

        # Footer Match Stats (Pushed to absolute bottom)
        self.draw_match_footer(surface, rect.x + config.s(30), rect.bottom - config.s(100), font_body, match_telemetry)

    def draw_human_telemetry(self, surface, title, color, x, y, is_active, font_sub, font_body, mt):
        draw_text(surface, title, font_sub, color, x, y, center=False)
        if is_active:
            draw_text(surface, "ACTIVE TURN", font_body, config.THEME_HIGHLIGHT, x + config.s(200), y + config.s(4), center=False)
        y += config.s(55)
        
        spacing = config.s(40)
        text_alpha = 255 if is_active else 120
        
        def draw_live_stat(label, val, col=config.WHITE, extra_y=0):
            surf = font_body.render(f"{label}: {val}", True, col)
            if text_alpha < 255:
                temp = surf.copy()
                temp.set_alpha(text_alpha)
                surface.blit(temp, (x, y + extra_y))
            else:
                surface.blit(surf, (x, y + extra_y))

        draw_live_stat("Status", mt['status'])
        y += spacing
        draw_live_stat("Longest Chain", mt['longest_chain'])
        y += spacing
        last_col_str = str(mt['last_col'] + 1) if mt['last_col'] != -1 else "None"
        draw_live_stat("Last Move Col", last_col_str)

    def draw_match_footer(self, surface, x, y, font_body, mt):
        pygame.draw.line(surface, (*config.THEME_ACCENT_1, 80), (x, y), (x + config.s(360), y), config.s(1))
        y += config.s(20)
        
        def draw_live_stat(label, val, col=config.WHITE):
            surf = font_body.render(f"{label}: {val}", True, col)
            surface.blit(surf, (x, y))

        draw_live_stat("Match Time", f"{mt['duration']:.1f}s", config.THEME_HIGHLIGHT)
        y += config.s(30)
        draw_live_stat("Total Moves", mt['total_moves'], config.WHITE)
        y += config.s(30)
        mode_str = "Human vs Human" if mt['mode'] == MODE_H_VS_H else "Human vs AI" if mt['mode'] == MODE_H_VS_AI else "AI vs AI"
        draw_live_stat("Mode", mode_str, (180, 180, 220))

    def draw_stats(self, surface, stats, title, color, x, y, is_active, font_sub, font_body):
        # 1. Title with Active Glow
        draw_text(surface, title, font_sub, color, x, y, center=False)
        
        if is_active:
            pulse = abs(math.sin(time.time() * 6)) * 155 + 100
            # Thinking indicator with blinking effect
            indicator_text = f"THINKING [Col {stats.thinking_move+1 if stats.thinking_move is not None else '?'}]"
            glow_surf = font_body.render(indicator_text, True, config.THEME_ACCENT_2)
            glow_surf.set_alpha(int(pulse))
            surface.blit(glow_surf, (x + config.s(180), y + config.s(4)))
        
        y += config.s(50)
        spacing = config.s(32) # Tightened spacing to fit panel
        
        # 2. Dynamic Search Data (Update opacity for inactive)
        text_alpha = 255 if is_active else 120
        
        def draw_live_stat(label, val, col=config.WHITE, extra_y=0):
            surf = font_body.render(f"{label}: {val}", True, col)
            if text_alpha < 255:
                # Manual alpha blending for inactive
                temp = surf.copy()
                temp.set_alpha(text_alpha)
                surface.blit(temp, (x, y + extra_y))
            else:
                surface.blit(surf, (x, y + extra_y))

        draw_live_stat("Algorithm", stats.algorithm)
        y += spacing
        draw_live_stat("Search Depth", stats.depth)
        y += spacing
        draw_live_stat("Nodes Explored", f"{stats.nodes_explored:,}")
        y += spacing
        draw_live_stat("Branches Pruned", f"{stats.branches_pruned:,}")
        y += spacing
        
        time_taken = stats.end_time - stats.start_time if stats.end_time else time.time() - stats.start_time
        nps = stats.nodes_explored / time_taken if time_taken > 0.001 else 0
        
        draw_live_stat("Eval Time", f"{time_taken:.3f}s")
        y += spacing
        draw_live_stat("Nodes/Sec", f"{nps:,.0f}")
        y += spacing
        
        # Highlight best score
        score_color = config.THEME_HIGHLIGHT if is_active else (150, 150, 50)
        draw_live_stat("Best Move Score", stats.best_score, score_color)
        
        # 3. Eval Bar Update (only if active)
        if is_active:
            self.eval_bar.update(stats.best_score)
            
        y += spacing + config.s(15)
        pygame.draw.line(surface, (*config.THEME_ACCENT_1, 100), (x, y), (x + config.s(360), y), config.s(1))

class EvalBar:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(config.s(x), config.s(y), config.s(width), config.s(height))
        self.current_eval = 0 # 0 is balanced, +ve is P1, -ve is P2
        self.target_eval = 0
        
    def update(self, val):
        # Normalize val to range [-1, 1] for visual bar
        # Assuming scores around 10000 are strong advantage
        norm = max(-1, min(1, val / 50000))
        self.target_eval = norm
        # Smooth interpolation
        self.current_eval += (self.target_eval - self.current_eval) * 0.1
        
    def draw(self, surface):
        # Draw background
        pygame.draw.rect(surface, (20, 20, 30), self.rect, border_radius=config.s(4))
        
        # Draw the bar split
        center_y = self.rect.centery
        # Advantage P1 (Top half)
        if self.current_eval > 0:
            h = (self.current_eval) * (self.rect.height / 2)
            bar_rect = pygame.Rect(self.rect.x, center_y - h, self.rect.width, h)
            pygame.draw.rect(surface, config.PLAYER1_COLOR, bar_rect)
        elif self.current_eval < 0:
            h = abs(self.current_eval) * (self.rect.height / 2)
            bar_rect = pygame.Rect(self.rect.x, center_y, self.rect.width, h)
            pygame.draw.rect(surface, config.PLAYER2_COLOR, bar_rect)
            
        # Draw center line
        pygame.draw.line(surface, config.WHITE, (self.rect.x, center_y), (self.rect.right, center_y), config.s(1))
        # Outer border
        pygame.draw.rect(surface, (*config.THEME_ACCENT_1, 100), self.rect, config.s(1), border_radius=config.s(4))

class HistoryList:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(config.s(x), config.s(y), config.s(width), config.s(height))
        self.scroll_y = 0
        self.item_height = 100
        
    def draw(self, surface, history_data):
        font_main = get_font("segoe ui", 20, bold=True)
        font_sub = get_font("segoe ui", 16)
        
        clip_rect = self.rect.copy()
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        for i, match in enumerate(history_data):
            iy = self.rect.y + i * config.s(self.item_height) + self.scroll_y
            item_rect = pygame.Rect(self.rect.x + config.s(10), iy, self.rect.width - config.s(20), config.s(90))
            
            if item_rect.bottom < self.rect.top or item_rect.top > self.rect.bottom:
                continue
                
            # Card Background (Dark Navy, no gold fill)
            pygame.draw.rect(surface, (10, 12, 25, 240), item_rect, border_radius=config.s(10))
            # Thin Gold Border
            pygame.draw.rect(surface, (*config.THEME_ACCENT_1, 100), item_rect, max(1, config.s(1)), border_radius=config.s(10))
            
            # Hover Glow
            mouse_pos = pygame.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, (*config.THEME_ACCENT_1, 40), item_rect.inflate(config.s(4), config.s(4)), max(1, config.s(2)), border_radius=config.s(12))
            
            # Winner Icon
            winner = match.get('winner', 0)
            win_color = config.PLAYER1_COLOR if winner == 1 else config.PLAYER2_COLOR if winner == 2 else config.WHITE
            pygame.draw.circle(surface, win_color, (item_rect.x + config.s(40), item_rect.centery), config.s(15))
            
            # Match Info
            mode_str = match.get('mode_str', "Unknown")
            date_str = match.get('date', "Date unknown")
            winner_idx = match.get('winner', 0)
            winner_text = "PLAYER 1 WINS" if winner_idx == 1 else "PLAYER 2 WINS" if winner_idx == 2 else "DRAW / TIE"
            
            draw_text(surface, mode_str, font_main, config.WHITE, item_rect.x + config.s(80), item_rect.y + config.s(20), center=False)
            draw_text(surface, winner_text, font_sub, win_color, item_rect.x + config.s(80), item_rect.y + config.s(45), center=False)
            draw_text(surface, date_str, font_sub, (140, 140, 160), item_rect.x + config.s(80), item_rect.y + config.s(65), center=False)
            
            # Stats on right
            stats_str = f"{match.get('total_moves', 0)} Moves | {int(match.get('duration', 0))}s"
            draw_text(surface, stats_str, font_sub, config.THEME_HIGHLIGHT, item_rect.right - config.s(20), item_rect.centery, center=False, align_right=True)

        surface.set_clip(old_clip)

