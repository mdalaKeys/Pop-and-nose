# Import
import pygame
import SceneManager
from Button import ButtonImg


def Menu():
    # Initialize
    pygame.init()
    pygame.event.clear()

    # Create Window/Display
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("My Awesome Game")

    # Initialize Clock for FPS
    fps = 30
    clock = pygame.time.Clock()

    # Images
    imgBackground = pygame.image.load('../Project - Balloon Pop/BackgroundBalloonPop.png').convert()

    # Buttons
    buttonStart = ButtonImg((465, 420), 'Project - Balloon Pop/ButtonStart.png',
                            pathSoundClick='Sounds/click.mp3',
                            pathSoundHover='Sounds/hover.mp3')

    # Load Music
    pygame.mixer.pre_init()
    pygame.mixer.music.load("../Project - Balloon Pop/BackgroundMusicMenu.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    # Main loop
    start = True
    while start:
        # Get Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    SceneManager.OpenScene("Game")

        # Apply Logic
        window.blit(imgBackground, (0, 0))
        buttonStart.draw(window)

        if buttonStart.state == 'clicked':
            pygame.mixer.music.stop()
            SceneManager.OpenScene("Game")

        # Update Display
        pygame.display.update()
        # Set FPS
        clock.tick(fps)


if __name__ == "__main__":
    Menu()
