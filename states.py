import pygame
import time
import math
import threading
import random
from config import config, BASE_WIDTH, BASE_HEIGHT, ROWS, COLS, EMPTY, PLAYER, AI_AGENT, MODE_H_VS_AI, MODE_AI_VS_AI, MODE_H_VS_H, DIFF_MEDIUM, DIFF_HARD, AI_MOVE_DELAY
from ui import draw_text, draw_elegant_text, Button, ParticleSystem, AI_Panel, get_font, GlassPanel, ConstellationSystem, CloudSystem, HistoryList, EvalBar
from board import Board
from ai import AI
from audio import audio_sys
from history import history_manager

class CinematicIntro:
    def __init__(self, screen):
        self.screen = screen
        self.start_time = time.time()
        self.duration = 8.0
        self.done = False
        self.constellations = ConstellationSystem(45) # Increased stars
        self.clouds = CloudSystem(6) # More atmospheric clouds
        self.particles = ParticleSystem(60) # Increased ambient particles
        self.logo_alpha = 0
        self.studio_alpha = 0
        self.title_alpha = 0
        self.screen_fade = 255 # Start dark
        self.logo_angle = 0
        self.zoom = 1.0
        audio_sys.play_sfx('intro')
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.done = True

    def draw_neural_logo(self, surface, x, y, size, alpha):
        """Draws a mathematically precise neural-network constellation symbol (THICKER & SHARPER)"""
        points = []
        nodes = 5
        # 1. Calculate positions for perfect symmetry
        for i in range(nodes):
            angle = math.radians(i * (360/nodes) + self.logo_angle)
            px = x + math.cos(angle) * size
            py = y + math.sin(angle) * size
            points.append((px, py))
            
        # 2. Draw Connections (EVERY outer node connects DIRECTLY to the center hub)
        # Thicker high-visibility lines
        line_color = (255, 255, 255, alpha)
        for p in points:
            # Main core line (thicker)
            pygame.draw.line(surface, line_color, (x, y), p, config.s(2))
            # Stronger glow for the line
            pygame.draw.line(surface, (255, 255, 255, alpha // 2), (x, y), p, config.s(5))
            
        # 3. Draw Central Hub (Thicker)
        pygame.draw.circle(surface, (255, 255, 255, alpha), (x, y), config.s(6))
        pygame.draw.circle(surface, (255, 255, 255, alpha // 2), (x, y), config.s(15), config.s(2))
            
        # 4. Draw Outer Nodes (White core with thicker glows)
        for p in points:
            pygame.draw.circle(surface, (*config.WHITE, alpha), p, config.s(5))
            pygame.draw.circle(surface, (255, 255, 255, alpha // 2), p, config.s(10), config.s(2))

    def update_and_draw(self):
        self.screen.fill(config.BG_COLOR)
        elapsed = time.time() - self.start_time
        
        if elapsed > self.duration:
            self.done = True
            
        cx, cy = config.s((BASE_WIDTH // 2, BASE_HEIGHT // 2))
        
        # 1. Background Atmosphere (Clouds/Stars)
        bg_alpha = 255
        if elapsed > self.duration - 1.0:
            bg_alpha = max(0, int(255 * (self.duration - elapsed)))
            
        self.clouds.update_and_draw(self.screen)
        self.constellations.update_and_draw(self.screen, bg_alpha)
        self.particles.update_and_draw(self.screen)
        
        # 2. Intro Sequence logic
        self.logo_angle += 0.2
        
        # Logo and Studio name fade (Sequential)
        if elapsed < 4.0:
            # Sequential timing: logo starts at 0, studio starts at 1.8
            self.logo_alpha = max(0, min(255, int((elapsed / 1.5) * 255)))
            
            # 1. Holographic Ring with Soft Border Glow (Fully transparent inside)
            pulse_val = abs(math.sin(time.time() * 1.5))
            logo_glow = int(pulse_val * 90 + 90) # Balanced cinematic glow
            glow_surf = pygame.Surface((config.s(400), config.s(400)), pygame.SRCALPHA)
            
            # Draw thin purple circular ring (High Visibility Outline)
            ring_color = (200, 100, 255, self.logo_alpha) 
            pygame.draw.circle(glow_surf, ring_color, (config.s(200), config.s(200)), config.s(140), config.s(2)) 
            
            # Substrate glow aura for the ring border
            for i in range(15): # Higher density for smooth cinematic glow
                g_alpha = int(logo_glow * (1 - i / 15) * (self.logo_alpha / 255) * 0.4)
                # Pure glowing purple aura
                pygame.draw.circle(glow_surf, (180, 60, 255, g_alpha), (config.s(200), config.s(200)), config.s(140 + i*1.2), config.s(1))
                
            self.screen.blit(glow_surf, (cx - config.s(200), cy - config.s(230)))
            
            # Draw Logo Emblem
            logo_surf = pygame.Surface((config.s(300), config.s(300)), pygame.SRCALPHA)
            self.draw_neural_logo(logo_surf, config.s(150), config.s(150), config.s(70), self.logo_alpha)
            self.screen.blit(logo_surf, (cx - config.s(150), cy - config.s(180)))
            
            # Draw AstraMind Studios & Subtitle (PERFECTLY SYNCHRONIZED)
            # Both texts fade in together at the same time as the logo
            self.studio_alpha = self.logo_alpha
            
            # 1. Main Studio Title
            font_med = get_font("segoe ui", 42)
            surf = font_med.render("AstraMind Studios", True, (240, 240, 255))
            surf.set_alpha(self.studio_alpha)
            rect = surf.get_rect(center=(cx, cy + config.s(80)))
            self.screen.blit(surf, rect)
            
            # 2. Subtitle (Appear TOGETHER with title at the same time)
            font_sub = get_font("segoe ui", 22) 
            sub_color = (250, 235, 190) # Yellowish Gold
            
            # Unified Fade and Glow
            sub_glow_alpha = int(40 * (self.studio_alpha / 255))
            glow_surf = font_sub.render("AI GAME SYSTEMS & INTERACTIVE SIMULATIONS", True, (*sub_color, sub_glow_alpha))
            self.screen.blit(glow_surf, glow_surf.get_rect(center=(cx, cy + config.s(118))))
            
            sub_surf = font_sub.render("AI GAME SYSTEMS & INTERACTIVE SIMULATIONS", True, sub_color)
            sub_surf.set_alpha(self.studio_alpha) # Exactly the same alpha
            sub_rect = sub_surf.get_rect(center=(cx, cy + config.s(118)))
            self.screen.blit(sub_surf, sub_rect)
            
        else:
            # Title fade
            self.title_alpha = max(0, min(255, int(((elapsed - 4.5) / 1.5) * 255)))
            
            self.zoom = 1.0 + (elapsed - 4.5) * 0.005 # Subtle zoom
            
            scale = min(1.0, 0.95 + ((elapsed - 4.5) * 0.02)) * self.zoom
            font_title = get_font("segoe ui", int(110 * scale), bold=True)
            
            # Sharp White Title with enhanced soft glow
            title_color = (255, 255, 255)
            # Soft title glow layers
            for i in range(4):
                g_alpha = int(abs(math.sin(time.time() * 2)) * 30 / (i + 1))
                draw_elegant_text(self.screen, "CONNECT4", font_title, (255, 255, 255, g_alpha), cx, cy - config.s(50), 3 + i)
            draw_elegant_text(self.screen, "CONNECT4", font_title, (255, 255, 255), cx, cy - config.s(50), 3)
            
            # Cinematic Muted Gold (Slightly darker, premium tone)
            font_sub = get_font("segoe ui", 36, bold=True)
            muted_gold = (190, 160, 90)
            sub_surf = font_sub.render("Neural Arena", True, muted_gold)
            sub_surf.set_alpha(self.title_alpha)
            sub_rect = sub_surf.get_rect(center=(cx, cy + config.s(55)))
            self.screen.blit(sub_surf, sub_rect)
            
            # Elegant Horizontal Divider Lines (Muted Gold)
            if self.title_alpha > 50:
                line_alpha = self.title_alpha // 3
                line_y = cy + config.s(55)
                # Left Divider
                pygame.draw.line(self.screen, (*muted_gold, line_alpha), (cx - config.s(240), line_y), (cx - config.s(120), line_y), config.s(1))
                # Right Divider
                pygame.draw.line(self.screen, (*muted_gold, line_alpha), (cx + config.s(120), line_y), (cx + config.s(240), line_y), config.s(1))

        # 3. Overall Screen Transition
        if elapsed < 1.0:
            self.screen_fade = int(255 * (1 - elapsed))
        elif elapsed > self.duration - 1.0:
            self.screen_fade = int(255 * (elapsed - (self.duration - 1.0)))
        else:
            self.screen_fade = 0
            
        if self.screen_fade > 0:
            fade_surf = pygame.Surface((config.s(BASE_WIDTH), config.s(BASE_HEIGHT)))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.screen_fade)
            self.screen.blit(fade_surf, (0, 0))

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.particles = ParticleSystem(120) # Increased star density for menu
        self.clouds = CloudSystem(12) # More visible menu clouds
        self.done = False
        self.mode = None
        self.p1_diff = DIFF_MEDIUM
        self.p2_diff = DIFF_HARD
        
        self.init_ui()
        
    def init_ui(self):
        btn_w, btn_h = 320, 70
        start_y = 380
        spacing = 90
        
        cx = BASE_WIDTH // 2
        
        self.buttons = [
            Button(cx - btn_w//2, start_y, btn_w, btn_h, "Human vs AI", "THEME_ACCENT_1", 26, action=True, value=MODE_H_VS_AI),
            Button(cx - btn_w//2, start_y + spacing, btn_w, btn_h, "AI vs AI", "THEME_ACCENT_1", 26, action=True, value=MODE_AI_VS_AI),
            Button(cx - btn_w//2, start_y + spacing*2, btn_w, btn_h, "Human vs Human", "THEME_ACCENT_1", 26, action=True, value=MODE_H_VS_H),
            Button(cx - btn_w - 20, start_y + spacing*3.5, btn_w, btn_h, "Game History", "THEME_ACCENT_1", 22, action=True, value="history"),
            Button(cx + 20, start_y + spacing*3.5, btn_w, btn_h, "Themes", "THEME_ACCENT_1", 22, action=True, value="themes"),
        ]
        
        self.buttons[0].icon_type = 'human_ai'
        self.buttons[1].icon_type = 'ai_ai'
        self.buttons[2].icon_type = 'human_human'
        
        # Difficulties side panels
        diff_w, diff_h = 130, 45
        diffs = ["Easy", "Med", "Hard", "Expert", "Imposs"]
        
        self.p1_diff_btns = []
        for i, d in enumerate(diffs):
            b = Button(cx - 520, 420 + i*55, diff_w, diff_h, d, "PLAYER1_COLOR", 18, action=True, value=i+1, is_toggle=True)
            if i + 1 == self.p1_diff: b.active = True
            self.p1_diff_btns.append(b)
            
        self.p2_diff_btns = []
        for i, d in enumerate(diffs):
            b = Button(cx + 390, 420 + i*55, diff_w, diff_h, d, "PLAYER2_COLOR", 18, action=True, value=i+1, is_toggle=True)
            if i + 1 == self.p2_diff: b.active = True
            self.p2_diff_btns.append(b)
            
        self.p1_panel = GlassPanel(cx - 570, 320, 230, 400)
        self.p2_panel = GlassPanel(cx + 340, 320, 230, 400)
        
        # New Popup states
        self.show_history = False
        self.show_themes = False
        self.history_list = HistoryList(BASE_WIDTH//2 - 400, 200, 800, 600)
        self.history_panel = GlassPanel(BASE_WIDTH//2 - 450, 100, 900, 800)
        
        self.theme_btns = []
        theme_names = list(config.themes.keys())
        for i, t in enumerate(theme_names):
            self.theme_btns.append(Button(BASE_WIDTH//2 - 150, 250 + i*80, 300, 60, t, "THEME_ACCENT_1", 22, action=True, value=f"set_theme_{t}"))

    def handle_events(self, events):
        for event in events:
            # 1. Process Popups FIRST (Layered UI approach)
            if self.show_history or self.show_themes:
                if event.type == pygame.MOUSEWHEEL and self.show_history:
                    self.history_list.scroll_y += event.y * 40
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.show_history and not self.history_panel.rect.inflate(config.s(20), config.s(20)).collidepoint(pos): 
                        self.show_history = False
                        return # Consume event
                    if self.show_themes:
                        clicked_theme = False
                        for btn in self.theme_btns:
                            if btn.rect.collidepoint(pos): clicked_theme = True
                        if not clicked_theme: 
                            self.show_themes = False
                            return # Consume event

                if self.show_themes:
                    for btn in self.theme_btns:
                        val = btn.handle_event(event)
                        if val and val.startswith("set_theme_"):
                            config.apply_theme(val.replace("set_theme_", ""))
                            self.show_themes = False
                            audio_sys.play_sfx('click')
                            return 
                # If popup is active, don't process anything else
                continue 

            # 2. Process Main UI if no popup is active
            for btn in self.buttons:
                val = btn.handle_event(event)
                if val:
                    if val == "history": self.show_history = True
                    elif val == "themes": self.show_themes = True
                    else:
                        self.mode = val
                        self.done = True
                        
            for btn in self.p1_diff_btns:
                val = btn.handle_event(event)
                if val:
                    self.p1_diff = val
                    for b in self.p1_diff_btns: b.active = (b.value == val)
                    
            for btn in self.p2_diff_btns:
                val = btn.handle_event(event)
                if val:
                    self.p2_diff = val
                    for b in self.p2_diff_btns: b.active = (b.value == val)

    def update_and_draw(self):
        self.screen.fill(config.BG_COLOR)
        
        # Nebula Haze behind title area
        haze_surf = pygame.Surface((config.s(600), config.s(300)), pygame.SRCALPHA)
        pygame.draw.ellipse(haze_surf, (180, 50, 200, 15), haze_surf.get_rect())
        self.screen.blit(haze_surf, (config.s(BASE_WIDTH//2 - 300), config.s(80)))
        
        self.clouds.update_and_draw(self.screen)
        self.particles.update_and_draw(self.screen)
        
        cx = config.s(BASE_WIDTH//2)
        
        draw_elegant_text(self.screen, "CONNECT4", get_font("segoe ui", 110, bold=True), config.WHITE, cx, config.s(160), 4)
        draw_elegant_text(self.screen, "NEURAL ARENA", get_font("segoe ui", 35, bold=True), config.THEME_ACCENT_1, cx, config.s(250), 2)
        
        self.p1_panel.draw(self.screen)
        p1_title_color = config.WHITE
        if self.mode == MODE_H_VS_AI: p1_title_color = config.THEME_HIGHLIGHT # Highlight active panel context
        draw_elegant_text(self.screen, "P1 (Red) Diff", get_font("segoe ui", 22, bold=True), p1_title_color, config.s(BASE_WIDTH//2 - 455), config.s(360), 2)
        for btn in self.p1_diff_btns:
            btn.draw(self.screen)
            
        self.p2_panel.draw(self.screen)
        draw_elegant_text(self.screen, "P2 (Yellow) Diff", get_font("segoe ui", 22, bold=True), config.WHITE, config.s(BASE_WIDTH//2 + 455), config.s(360), 2)
        for btn in self.p2_diff_btns:
            btn.draw(self.screen)
        
        for btn in self.buttons:
            btn.draw(self.screen)
            
        if self.show_history:
            self.history_panel.draw(self.screen)
            draw_elegant_text(self.screen, "MATCH HISTORY", get_font("segoe ui", 40, bold=True), config.WHITE, config.s(BASE_WIDTH//2), config.s(160), 3)
            self.history_list.draw(self.screen, history_manager.get_history())
            
        if self.show_themes:
            overlay = pygame.Surface(config.s((BASE_WIDTH, BASE_HEIGHT)), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            draw_elegant_text(self.screen, "SELECT THEME", get_font("segoe ui", 50, bold=True), config.THEME_ACCENT_1, config.s(BASE_WIDTH//2), config.s(180), 3)
            for btn in self.theme_btns:
                btn.draw(self.screen)
            
        self._draw_footer()

    def _draw_footer(self):
        footer_h = config.s(100)
        footer_y = config.s(BASE_HEIGHT) - footer_h
        
        # 1. Dark Glossy Background (Thicker presence)
        footer_rect = pygame.Rect(0, footer_y, config.s(BASE_WIDTH), footer_h)
        s = pygame.Surface(footer_rect.size, pygame.SRCALPHA)
        s.fill((8, 8, 20, 245)) # Slightly more opaque and deep
        
        # Thicker premium glow at the top edge
        for i in range(config.s(6)):
            alpha = int(100 * (1 - i / 6))
            pygame.draw.line(s, (180, 50, 255, alpha), (0, i), (footer_rect.width, i), config.s(1))
            
        self.screen.blit(s, footer_rect)
        
        # Left Side: Taglines (Increase padding)
        font_tag = get_font("segoe ui", 22, bold=True)
        font_sub = get_font("segoe ui", 14)
        
        draw_elegant_text(self.screen, "Strategize. Connect. Conquer.", font_tag, config.WHITE, config.s(80), footer_y + config.s(35), center=False)
        draw_text(self.screen, "Outsmart the AI. Rule the Neural Arena.", font_sub, (180, 180, 200), config.s(80), footer_y + config.s(65), center=False)
        
        # separator line
        pygame.draw.line(self.screen, (255, 255, 255, 20), (config.s(450), footer_y + config.s(20)), (config.s(450), footer_y + config.s(80)), 1)
        
        # 3. Center: Glowing Neural Emblem (Slow Rotation)
        self._draw_emblem(config.s(BASE_WIDTH // 2), footer_y + footer_h // 2)
        
        # separator line
        pygame.draw.line(self.screen, (255, 255, 255, 20), (config.s(BASE_WIDTH - 450), footer_y + config.s(20)), (config.s(BASE_WIDTH - 450), footer_y + config.s(80)), 1)
        
        # 4. Right Side: Controls
        font_ctrl = get_font("segoe ui", 18, bold=True)
        draw_elegant_text(self.screen, "[F11] Fullscreen   [ESC] Exit", font_ctrl, config.THEME_ACCENT_1, config.s(BASE_WIDTH - 80), footer_y + footer_h // 2, center=True)

    def _draw_emblem(self, x, y):
        """Thicker, Sharper premium emblem for the footer"""
        size = config.s(40)
        glow_color = (200, 80, 255) # More vibrant Purple
        
        # 1. Strong Circular Purple Glow
        glow_surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
        for i in range(8):
            alpha = int(60 * (1 - i / 8))
            rad = int(size * (0.8 + 0.4 * i / 8))
            pygame.draw.circle(glow_surf, (*glow_color, alpha), (size*1.5, size*1.5), rad)
        self.screen.blit(glow_surf, (x - size*1.5, y - size*1.5))
        
        # 2. Refined Neural Network Symbol (Thicker Lines)
        ring_rad = config.s(8)
        # Ring core
        pygame.draw.circle(self.screen, (240, 200, 255, 230), (x, y), ring_rad, config.s(2))
        
        node_count = 5
        outer_rad = config.s(24)
        for i in range(node_count):
            angle = math.radians(i * (360 / node_count) - 90)
            nx = x + math.cos(angle) * outer_rad
            ny = y + math.sin(angle) * outer_rad
            
            # Thicker Glowing Lines
            pygame.draw.line(self.screen, (220, 150, 255, 180), (x, y), (nx, ny), config.s(2))
            
            # Sharper Outer Nodes
            pygame.draw.circle(self.screen, (255, 255, 255, 220), (int(nx), int(ny)), config.s(4))
            pygame.draw.circle(self.screen, config.WHITE, (int(nx), int(ny)), config.s(2))

class GameState:
    def __init__(self, screen, mode, p1_diff, p2_diff):
        self.screen = screen
        self.mode = mode
        self.board = Board()
        self.turn = 0
        self.game_over = False
        self.winner = None
        self.particles = ParticleSystem(50)
        self.clouds = CloudSystem(10)
        
        self.sq_size = 120
        self.radius = self.sq_size // 2 - 12
        self.board_w = COLS * self.sq_size
        self.board_h = ROWS * self.sq_size
        
        self.margin_left = (BASE_WIDTH - 450 - self.board_w) // 2
        self.header_h = 220
        
        self.ai_panel = AI_Panel(BASE_WIDTH - 450, 100, 420, 850)
        
        # Hint Button Setup
        self.hint_btn = Button(50, 120, 160, 55, "Hint", "THEME_ACCENT_1", 22, action=True, value="hint")
        self.hint_col = None
        self.hint_time = 0
        self.hint_cooldown = 0
        
        self.p1_is_ai = (mode == MODE_AI_VS_AI)
        self.p2_is_ai = (mode == MODE_H_VS_AI or mode == MODE_AI_VS_AI)
        
        self.ai_p1 = AI(p1_diff) if self.p1_is_ai else None
        self.ai_p2 = AI(p2_diff) if self.p2_is_ai else None
        
        self.ai_thread = None
        self.ai_result_col = None
        
        self.hover_col = None
        
        self.buttons = [
            Button(50, 50, 160, 55, "Menu", "THEME_ACCENT_1", 22, action=True, value="menu"),
            Button(230, 50, 160, 55, "Restart", "THEME_ACCENT_1", 22, action=True, value="restart")
        ]
        
        self.return_to_menu = False
        self.animating_drop = False
        self.drop_anim_r = 0
        self.drop_anim_c = 0
        self.drop_anim_piece = 0
        self.drop_anim_y = 0
        self.target_y = 0
        
        self.last_move_time = time.time()
        
        # Match Telemetry Data
        self.start_match_time = time.time()
        self.total_moves = 0
        self.last_col = -1
        self.longest_chain = 0
        self.match_status = "Game In Progress"

    def start_ai_turn(self):
        if self.game_over or self.ai_thread is not None or self.animating_drop:
            return
            
        current_ai = self.ai_p1 if self.turn == 0 else self.ai_p2
        piece = PLAYER if self.turn == 0 else AI_AGENT
        
        def ai_worker():
            col = current_ai.get_best_move(self.board, piece)
            self.ai_result_col = col

        self.ai_thread = threading.Thread(target=ai_worker)
        self.ai_thread.daemon = True
        self.ai_thread.start()

    def handle_events(self, events):
        pos = pygame.mouse.get_pos()
        lx = pos[0] / config.scale_factor
        ly = pos[1] / config.scale_factor
        
        self.hover_col = None
        if lx >= self.margin_left and lx < self.margin_left + self.board_w and ly >= self.header_h and not self.game_over and not self.animating_drop:
            self.hover_col = int((lx - self.margin_left) // self.sq_size)

        for event in events:
            for btn in self.buttons:
                val = btn.handle_event(event)
                if val == "menu":
                    self.return_to_menu = True
                elif val == "restart":
                    self.__init__(self.screen, self.mode, self.ai_p1.difficulty if self.ai_p1 else DIFF_MEDIUM, self.ai_p2.difficulty if self.ai_p2 else DIFF_HARD)

            if self.mode == MODE_H_VS_AI and not self.game_over:
                if self.hint_btn.handle_event(event) == "hint":
                    if time.time() - self.hint_cooldown > 5.0:
                        self.hint_cooldown = time.time()
                        temp_ai = AI(DIFF_HARD)
                        self.hint_col = temp_ai.get_best_move(self.board, PLAYER)
                        self.hint_time = time.time()
                        audio_sys.play_sfx('click')
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.game_over and not self.animating_drop and self.hover_col is not None:
                    current_is_ai = (self.turn == 0 and self.p1_is_ai) or (self.turn == 1 and self.p2_is_ai)
                    if not current_is_ai:
                        if self.board.is_valid_location(self.hover_col):
                            self.process_move(self.hover_col)

    def process_move(self, col):
        row = self.board.get_next_open_row(col)
        piece = PLAYER if self.turn == 0 else AI_AGENT
        
        self.animating_drop = True
        self.drop_anim_r = row
        self.drop_anim_c = col
        self.drop_anim_piece = piece
        self.drop_anim_y = self.header_h - self.sq_size
        self.target_y = self.header_h + row * self.sq_size + self.sq_size//2
        
        self.board.drop_piece(row, col, piece)
        audio_sys.play_sfx('drop')
        self.last_drop_time = time.time()
        
        # Update Telemetry
        self.total_moves += 1
        self.last_col = col
        self.longest_chain = self._calculate_longest_chain()
        self._update_match_status()

    def _calculate_longest_chain(self):
        max_chain = 0
        # Horizontal
        for r in range(ROWS):
            row_array = self.board.state[r, :]
            for c in range(COLS - 3):
                window = list(row_array[c:c+4])
                # Count max same pieces (excluding EMPTY)
                p1 = window.count(PLAYER)
                p2 = window.count(AI_AGENT)
                if window.count(EMPTY) + max(p1, p2) == 4:
                    max_chain = max(max_chain, p1, p2)
        # Vertical, Diagonal etc can be added, but horizontal/vertical is usually enough for a quick "stat"
        for c in range(COLS):
            col_array = self.board.state[:, c]
            for r in range(ROWS - 3):
                window = list(col_array[r:r+4])
                p1 = window.count(PLAYER)
                p2 = window.count(AI_AGENT)
                if window.count(EMPTY) + max(p1, p2) == 4:
                    max_chain = max(max_chain, p1, p2)
        return max_chain

    def _update_match_status(self):
        score = self.board.score_position(PLAYER)
        if score > 500: self.match_status = "Player 1 Leading"
        elif score < -500: self.match_status = "Player 2 Leading"
        elif self.total_moves > 20: self.match_status = "Strategic Deadlock"
        else: self.match_status = "Game In Progress"

    def finish_move(self):
        piece = PLAYER if self.turn == 0 else AI_AGENT
        
        if self.board.winning_move(piece):
            self.game_over = True
            self.winner = piece
            if self.mode == MODE_H_VS_AI and self.winner == AI_AGENT:
                audio_sys.play_sfx('defeat')
            else:
                audio_sys.play_sfx('victory')
        elif len(self.board.get_valid_locations()) == 0:
            self.game_over = True
            self.winner = 0 
            
        if self.game_over:
            # Save to history
            mode_str = "H vs AI" if self.mode == MODE_H_VS_AI else "AI vs AI" if self.mode == MODE_AI_VS_AI else "H vs H"
            history_manager.save_match({
                'mode': self.mode,
                'mode_str': mode_str,
                'winner': self.winner,
                'duration': time.time() - self.start_match_time,
                'total_moves': self.total_moves,
                'p1_diff': self.ai_p1.difficulty if self.ai_p1 else 0,
                'p2_diff': self.ai_p2.difficulty if self.ai_p2 else 0,
            })
        else:
            self.turn = (self.turn + 1) % 2
            
        self.animating_drop = False
        self.last_move_time = time.time()

    def _draw_disc(self, x, y, color, is_winning=False):
        """Draws a vibrant solid disc with metallic shading and edge shine"""
        sx, sy = config.s((x, y))
        rad = config.s(self.radius)
        
        # Win pulse animation
        if is_winning:
            pulse = abs(math.sin(time.time() * 6)) * 40
            glow_rad = rad + config.s(10 + pulse)
            glow_s = pygame.Surface((glow_rad*2, glow_rad*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (*color, 60), (glow_rad, glow_rad), glow_rad)
            self.screen.blit(glow_s, (sx - glow_rad, sy - glow_rad))
        
        # 1. Dark background shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 180), (sx, sy + config.s(4)), rad)
        
        # 2. Main Body with Radial Metallic Shine
        pygame.draw.circle(self.screen, color, (sx, sy), rad)
        
        # Highlight (metallic)
        highlight_s = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_s, (255, 255, 255, 60), (rad * 0.6, rad * 0.6), rad * 0.6)
        self.screen.blit(highlight_s, (sx - rad, sy - rad))
        
        # Edge Shine
        pygame.draw.circle(self.screen, (255, 255, 255, 80), (sx, sy), rad, config.s(2))
        
        # Inner rim
        inner_color = (max(0, color[0]-60), max(0, color[1]-60), max(0, color[2]-60))
        pygame.draw.circle(self.screen, inner_color, (sx, sy), rad - config.s(4), config.s(2))

    def update_and_draw(self):
        self.screen.fill(config.BG_COLOR)
        
        # 1. Background Environment (Clouds)
        self.clouds.update_and_draw(self.screen)
        self.particles.update_and_draw(self.screen)
        
        # AI Logic
        current_is_ai = (self.turn == 0 and self.p1_is_ai) or (self.turn == 1 and self.p2_is_ai)
        if not self.game_over and not self.animating_drop and current_is_ai:
            if time.time() - self.last_move_time > AI_MOVE_DELAY:
                if self.ai_thread is None:
                    self.start_ai_turn()
                elif not self.ai_thread.is_alive():
                    if self.ai_result_col is not None:
                        self.process_move(self.ai_result_col)
                    self.ai_thread = None
                    self.ai_result_col = None

        draw_elegant_text(self.screen, "NEURAL ARENA", get_font("segoe ui", 45, bold=True), config.WHITE, config.s(BASE_WIDTH//2 - 200), config.s(75), 3)
        
        # Turn indicator
        turn_text = "PLAYER 1'S TURN" if self.turn == 0 else "PLAYER 2'S TURN"
        turn_color = config.PLAYER1_COLOR if self.turn == 0 else config.PLAYER2_COLOR
        if current_is_ai: 
            turn_text = "AI IS THINKING..."
            # Neural pulse animation for AI
            pulse = abs(math.sin(time.time() * 5)) * 100
            pygame.draw.circle(self.screen, (*config.THEME_HIGHLIGHT, int(pulse)), config.s((BASE_WIDTH//2 - 200, 125)), config.s(10))
            
        draw_text(self.screen, turn_text, get_font("segoe ui", 24, bold=True), turn_color, config.s(BASE_WIDTH//2 - 200), config.s(125))
        
        for btn in self.buttons:
            btn.draw(self.screen)
            
        if self.mode == MODE_H_VS_AI and not self.game_over:
            self.hint_btn.draw(self.screen)
            # Hint pulsing effect
            if self.hint_col is not None and time.time() - self.hint_time < 3.0:
                hx = self.margin_left + self.hint_col * self.sq_size + self.sq_size // 2
                hy = self.header_h - self.sq_size // 2
                pulse = abs(math.sin(time.time() * 8)) * 100 + 100
                pygame.draw.circle(self.screen, (*config.THEME_HIGHLIGHT, int(pulse)), config.s((hx, hy)), config.s(self.radius + 5), config.s(3))
            
        if self.game_over:
            if self.winner == PLAYER:
                draw_elegant_text(self.screen, "PLAYER 1 WINS!", get_font("segoe ui", 70, bold=True), config.PLAYER1_COLOR, config.s(BASE_WIDTH//2 - 200), config.s(150), 4)
            elif self.winner == AI_AGENT:
                draw_elegant_text(self.screen, "PLAYER 2 WINS!", get_font("segoe ui", 70, bold=True), config.PLAYER2_COLOR, config.s(BASE_WIDTH//2 - 200), config.s(150), 4)
            else:
                draw_elegant_text(self.screen, "DRAW!", get_font("segoe ui", 70, bold=True), config.WHITE, config.s(BASE_WIDTH//2 - 200), config.s(150), 4)

        stat1 = self.ai_p1.stats if self.ai_p1 else None
        stat2 = self.ai_p2.stats if self.ai_p2 else None
        
        # Build telemetry for human vs human or general stats
        match_telemetry = {
            'turn': self.turn,
            'total_moves': self.total_moves,
            'duration': time.time() - self.start_match_time if not self.game_over else self.last_move_time - self.start_match_time,
            'last_col': self.last_col,
            'status': self.match_status,
            'longest_chain': self.longest_chain,
            'mode': self.mode
        }
        
        self.ai_panel.draw(self.screen, stat1, stat2, self.turn, self.mode, match_telemetry)

        # 2. Neural Board Rendering (High-Fidelity Navy Grid)
        board_rect = pygame.Rect(self.margin_left, self.header_h, self.board_w, self.board_h)
        sbr = pygame.Rect(config.s(board_rect.x), config.s(board_rect.y), config.s(board_rect.width), config.s(board_rect.height))
        
        # Board Outer Shadow
        shadow_rect = sbr.copy()
        shadow_rect.y += config.s(10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), shadow_rect, border_radius=config.s(20))
        
        # Board Body (Walnut Brown with Glass Effect)
        s_board = pygame.Surface((sbr.width, sbr.height), pygame.SRCALPHA)
        s_board.fill((*config.GRID_COLOR, 240))
        
        # Glossy reflection
        pygame.draw.polygon(s_board, (255, 255, 255, 15), [(0, 0), (sbr.width, 0), (sbr.width // 2, sbr.height), (0, sbr.height)])
        
        self.screen.blit(s_board, (sbr.x, sbr.y))
        
        # Soft Board Edge Glow
        pygame.draw.rect(self.screen, (*config.THEME_ACCENT_1, 40), sbr.inflate(config.s(10), config.s(10)), config.s(4), border_radius=config.s(22))
        
        # Arcade Bevel / Inner Highlight
        pygame.draw.rect(self.screen, (255, 255, 255, 40), sbr, config.s(2), border_radius=config.s(20))
        
        # 3. Hover Piece
        if self.hover_col is not None and not self.animating_drop and not current_is_ai and not self.game_over:
            x = self.margin_left + self.hover_col * self.sq_size + self.sq_size//2
            y = self.header_h - self.sq_size//2
            color = config.PLAYER1_COLOR if self.turn == 0 else config.PLAYER2_COLOR
            sx, sy = config.s((x, y))
            rad = config.s(self.radius)
            s_hover = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
            pygame.draw.circle(s_hover, (*color, 120), (rad, rad), rad)
            self.screen.blit(s_hover, (sx - rad, sy - rad))

        # 4. Animating Piece
        if self.animating_drop:
            x = self.margin_left + self.drop_anim_c * self.sq_size + self.sq_size//2
            self.drop_anim_y += 60
            if self.drop_anim_y >= self.target_y:
                # Add satisfying landing bounce
                bounce_elapsed = time.time() - self.last_drop_time
                if bounce_elapsed < 0.2:
                    self.drop_anim_y = self.target_y - (0.2 - bounce_elapsed) * 100
                else:
                    self.drop_anim_y = self.target_y
                    self.finish_move()
            color = config.PLAYER1_COLOR if self.drop_anim_piece == PLAYER else config.PLAYER2_COLOR
            self._draw_disc(x, self.drop_anim_y, color)

        # 5. Pieces on board & Holes
        for r in range(ROWS):
            for c in range(COLS):
                x = self.margin_left + c * self.sq_size + self.sq_size//2
                y = self.header_h + r * self.sq_size + self.sq_size//2
                
                piece_val = self.board.state[r][c]
                if piece_val == PLAYER:
                    if not (self.animating_drop and r == self.drop_anim_r and c == self.drop_anim_c):
                        self._draw_disc(x, y, config.PLAYER1_COLOR)
                elif piece_val == AI_AGENT:
                    if not (self.animating_drop and r == self.drop_anim_r and c == self.drop_anim_c):
                        self._draw_disc(x, y, config.PLAYER2_COLOR)
                else:
                    # Deep Holes with Rim Light and Inner Shadow
                    sx, sy = config.s((x, y))
                    rad = config.s(self.radius)
                    pygame.draw.circle(self.screen, (10, 5, 2), (sx, sy), rad)
                    
                    # Inner Shadow
                    shadow_s = pygame.Surface((rad*2, rad*2), pygame.SRCALPHA)
                    pygame.draw.circle(shadow_s, (0, 0, 0, 100), (rad, rad), rad)
                    pygame.draw.circle(shadow_s, (0, 0, 0, 0), (rad + config.s(4), rad + config.s(4)), rad - config.s(4))
                    self.screen.blit(shadow_s, (sx - rad, sy - rad))
                    
                    # Hole Rim Light
                    pygame.draw.circle(self.screen, (80, 50, 30), (sx, sy), rad, config.s(2))

        # 6. Sharp Neural Border (Layered Gold & Glow)
        pygame.draw.rect(self.screen, config.THEME_ACCENT_1, sbr, max(1, config.s(4)), border_radius=config.s(20))
        # Outer substrate glow for the board
        for i in range(config.s(5)):
            a = int(30 * (1 - i / 5))
            # CRITICAL: width must be at least 1 to avoid fill
            pygame.draw.rect(self.screen, (*config.THEME_ACCENT_1, a), sbr.inflate(config.s(i*2), config.s(i*2)), max(1, config.s(1)), border_radius=config.s(20+i))

        # 7. Win line
        if self.game_over and self.winner != 0:
            win_line = self.board.get_winning_line(self.winner)
            if win_line:
                start_p = win_line[0]
                end_p = win_line[-1]
                sx1, sy1 = config.s((self.margin_left + start_p[1]*self.sq_size + self.sq_size//2, self.header_h + start_p[0]*self.sq_size + self.sq_size//2))
                sx2, sy2 = config.s((self.margin_left + end_p[1]*self.sq_size + self.sq_size//2, self.header_h + end_p[0]*self.sq_size + self.sq_size//2))
                pulse = abs(math.sin(time.time() * 5)) * 100
                pygame.draw.line(self.screen, config.THEME_HIGHLIGHT, (sx1, sy1), (sx2, sy2), config.s(10))
                pygame.draw.line(self.screen, (255, 255, 255, int(155 + pulse)), (sx1, sy1), (sx2, sy2), config.s(3))
                
                # Draw glowing discs for the winning line
                for r_win, c_win in win_line:
                    wx = self.margin_left + c_win * self.sq_size + self.sq_size//2
                    wy = self.header_h + r_win * self.sq_size + self.sq_size//2
                    color = config.PLAYER1_COLOR if self.winner == PLAYER else config.PLAYER2_COLOR
                    self._draw_disc(wx, wy, color, is_winning=True)
