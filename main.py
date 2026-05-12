import pygame
import sys
import asyncio
from config import config, BASE_WIDTH, BASE_HEIGHT, FPS
from states import CinematicIntro, MainMenu, GameState
from audio import audio_sys

async def main():
    print("Initializing Pygame...")
    pygame.init()
    pygame.display.set_caption("CONNECT4: Neural Arena")
    
    # Start in windowed mode initially, but user can press F11
    flags = pygame.RESIZABLE
    print("Setting up display...")
    screen = pygame.display.set_mode((1280, 720), flags)
    config.update_resolution(1280, 720, False)
    
    clock = pygame.time.Clock()
    print("Starting music...")
    audio_sys.start_music(gameplay=False) # Start with menu ambience

    STATE_INTRO = 0
    STATE_MENU = 1
    STATE_GAME = 2

    current_state = STATE_INTRO
    print("Initializing Intro state...")
    intro = CinematicIntro(screen)
    print("Initializing Menu state...")
    menu = MainMenu(screen)
    game = None

    print("Entering main loop...")
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not config.is_fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    config.update_resolution(event.w, event.h, False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == STATE_INTRO:
                        intro.done = True
                    elif current_state == STATE_GAME:
                        game.return_to_menu = True
                    else:
                        running = False
                elif event.key == pygame.K_F11:
                    config.is_fullscreen = not config.is_fullscreen
                    if config.is_fullscreen:
                        # Fullscreen borderless
                        display_info = pygame.display.Info()
                        w, h = display_info.current_w, display_info.current_h
                        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN | pygame.NOFRAME)
                        config.update_resolution(w, h, True)
                    else:
                        screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                        config.update_resolution(1280, 720, False)

        if current_state == STATE_INTRO:
            intro.handle_events(events)
            intro.update_and_draw()
            if intro.done:
                current_state = STATE_MENU

        elif current_state == STATE_MENU:
            menu.handle_events(events)
            menu.update_and_draw()
            if menu.done:
                game = GameState(screen, menu.mode, menu.p1_diff, menu.p2_diff)
                current_state = STATE_GAME
                audio_sys.start_music(gameplay=True) # Transition to gameplay ambience
                menu.done = False
                menu.mode = None

        elif current_state == STATE_GAME:
            game.handle_events(events)
            game.update_and_draw()
            if game.return_to_menu:
                current_state = STATE_MENU
                audio_sys.start_music(gameplay=False) # Transition back to menu ambience
                game.return_to_menu = False

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
