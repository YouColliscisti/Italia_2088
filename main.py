import asyncio
import pygame
from src.game import Game


async def main():
    game = Game()
    from src.settings import FPS
    game.running = True
    while game.running:
        dt = min(game.clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
                game.sound.toggle_mute()
                continue
            game.handle_event(event)

        #sfondo dinamico
        game.bg.update(dt)
        if game.state == "INTRO":
            game.draw_neon_intro()
        elif game.state == "MENU":
            game.draw_neon_main_menu()
        elif game.state == "CHARACTER_SELECT":
            game.bg.draw(game.screen, 1, game.selected_character)
            game.ui.draw_character_selection(game.save_mgr.get_completed_stories(), game.difficulty)
        elif game.state == "PLAYING" and game.level:
            result = game.level.run(dt)
            game.handle_level_result(result)


        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())

