# Import
import pygame

# Initialize
pygame.init()
pygame.mixer.pre_init()


class ToggleImg:
    def __init__(self, pos, pathImg, scale=1, pathSoundClick=None):

        # Loading Main Image
        img = pygame.image.load(pathImg).convert_alpha()
        width, height = img.get_size()
        img = pygame.transform.smoothscale(img, (int(width * scale), int(height * scale)))

        # Split image to get all frames
        width, height = img.get_size()
        heightSingleFrame = int(height / 2)
        imgList = []
        for i in range(2):
            imgCrop = img.subsurface((0, i * heightSingleFrame,
                                      width, heightSingleFrame))
            imgList.append(imgCrop)

        self.imgOff = imgList[0]
        self.imgOn = imgList[1]

        self.state = 'off'
        self.img = self.imgOff
        self.rectImg = self.imgOff.get_rect()
        self.rectImg.topleft = pos

        self.pathSoundClick = pathSoundClick
        if self.pathSoundClick is not None:
            self.soundClick = pygame.mixer.Sound(self.pathSoundClick)

        self.counter = -1

    def draw(self, window):
        # Get mouse position to check if inside button
        posMouse = pygame.mouse.get_pos()

        if self.rectImg.collidepoint(posMouse):
            if pygame.mouse.get_pressed()[0] and self.counter == -1:
                self.counter = 0
                if self.pathSoundClick is not None:
                    self.soundClick.play()
                if self.state == 'on':
                    self.state = 'off'
                else:
                    self.state = 'on'

        if self.counter != -1:
            self.counter += 1
            if self.counter > 5:
                self.counter = -1

        if self.state == 'on':
            self.img = self.imgOn
        else:
            self.img = self.imgOff

        window.blit(self.img, self.rectImg)


if __name__ == "__main__":

    # Create Window/Display
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("My Awesome Game")

    # Initialize Clock for FPS
    fps = 30
    clock = pygame.time.Clock()

    # Toggle
    toggleList = []
    for x in range(8):
        for y in range(9):
            toggleList.append(ToggleImg(((x * (100+50))+50, (y * 70)+50),
                                        "Toggle/ToggleGreen.png",
                                        pathSoundClick='Sounds/click.mp3'))

    # Main loop
    start = True
    while start:
        # Get Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()

        # Apply Logic
        window.fill((255, 255, 255))
        for toggle in toggleList:
            toggle.draw(window)
            print((toggle.state))
        # Update Display
        pygame.display.update()
        # Set FPS
        clock.tick(fps)
