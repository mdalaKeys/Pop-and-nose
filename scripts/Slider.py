# Import
import pygame

# Initialize
pygame.init()


class Slider:
    def __init__(self, pos, widthSlider=500, color=(0, 200, 0), startValue=50, min=0, max=100,
                 text=True, fontSize=50, fontColor=(100, 100, 100), fontPath=None):
        self.pos = pos
        self.widthSlider = widthSlider
        self.color = color
        self.value = startValue
        self.min = min
        self.max = max
        self.text = text
        self.fontPath = fontPath
        self.fontSize = fontSize
        self.fontColor = fontColor

        self.rectBack = pygame.Rect((self.pos[0], self.pos[1] - 10, self.widthSlider, 24))

    def convertValue(self, x, min1, max1, min2, max2):
        return int((x - min1) * (max2 - min2) / (max1 - min1) + min2)

    def draw(self, window):

        posMouse = pygame.mouse.get_pos()
        if self.rectBack.collidepoint(posMouse):  # in the slider region
            if pygame.mouse.get_pressed()[0]:  # left mouse is clicked
                self.value = self.convertValue(posMouse[0] - self.pos[0], 0, self.widthSlider,
                                               self.min, self.max)
                print(self.value)

        currentWidth = (self.value / (self.max - self.min)) * self.widthSlider
        # pygame.draw.rect(window,(200, 0, 0),rect=self.rectBack)
        pygame.draw.rect(window, (200, 200, 200),
                         (self.pos[0], self.pos[1], self.widthSlider, 5))
        pygame.draw.rect(window, self.color,
                         (self.pos[0], self.pos[1], currentWidth, 5))
        pygame.draw.circle(window, self.color, (self.pos[0] + currentWidth, self.pos[1] + 3),
                           12)

        if self.text:
            font = pygame.font.Font(self.fontPath, self.fontSize)
            myText = font.render(str(self.value), True, self.fontColor)
            textRect = myText.get_rect()
            # Center the Text
            textRect.x = self.pos[0] + self.widthSlider + 30
            textRect.centery = self.rectBack.centery
            window.blit(myText, textRect)


if __name__ == "__main__":
    # Create Window/Display
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("My Awesome Game")

    # Initialize Clock for FPS
    fps = 30
    clock = pygame.time.Clock()

    # Sliders
    slider1 = Slider((100, 100),widthSlider=1000,min=0, max = 600, startValue=300)
    slider2 = Slider((100, 300),color=(255,0,255))
    slider3 = Slider((100, 500),text = False)


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
        slider1.draw(window)
        slider2.draw(window)
        slider3.draw(window)
        # Update Display
        pygame.display.update()
        # Set FPS
        clock.tick(fps)
