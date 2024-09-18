# Import
import os
import random
import pygame
import SceneManager
import cv2
import numpy as np
import time
import mediapipe as mp
from Button import ButtonImg

class Balloon:
    def __init__(self, pos, path, scale=1, grid=(2, 4),
                 animationFrames=None, speedAnimation=1, speed=3, pathSoundPop=None):
        # Loading Main Image
        img = pygame.image.load(path).convert_alpha()
        width, height = img.get_size()
        img = pygame.transform.smoothscale(img, (int(width * scale), int(height * scale)))
        width, height = img.get_size()

        # Split image to get all frames
        if animationFrames is None:  # When animation frames is not defined then use all frames
            animationFrames = grid[0] * grid[1]
        widthSingleFrame = width / grid[1]
        heightSingleFrame = height / grid[0]
        self.imgList = []
        counter = 0
        for row in range(grid[0]):
            for col in range(grid[1]):
                counter += 1
                if counter <= animationFrames:
                    imgCrop = img.subsurface((col * widthSingleFrame, row * heightSingleFrame,
                                              widthSingleFrame, heightSingleFrame))
                    self.imgList.append(imgCrop)

        self.img = self.imgList[0]
        self.rectImg = self.img.get_rect()
        self.rectImg.x, self.rectImg.y = pos[0], pos[1]
        self.pos = pos
        self.path = path
        self.animationCount = 0
        self.speedAnimation = speedAnimation
        self.isAnimating = False
        self.speed = speed
        self.pathSoundPop = pathSoundPop
        if self.pathSoundPop:
            self.soundPop = pygame.mixer.Sound(self.pathSoundPop)
        self.pop = False

    def draw(self, window):
        if self.isAnimating is False:
            self.rectImg.y -= self.speed
        window.blit(self.img, self.rectImg)

    def checkPop(self, x, y):
        # Check for the hit
        if self.rectImg.collidepoint(x, y) and self.isAnimating is False:
            self.isAnimating = True
            if self.pathSoundPop:
                self.soundPop.play()

        if self.isAnimating:
            # Loop through all the frames
            if self.animationCount != len(self.imgList) - 1:
                self.animationCount += 1
                self.img = self.imgList[self.animationCount]
            else:
                self.pop = True

        if self.pop:
            return self.rectImg.y
        else:
            return None

def Game():
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

    # Webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # width
    cap.set(4, 720)  # height

    # Pose Estimation
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # Variables
    balloons = []
    startTime = time.time()
    generatorStartTime = time.time()
    generatorDelay = 1
    speed = 5
    score = 0
    totalTime = 30

    # Images
    imgScore = pygame.image.load('../Project - Balloon Pop/BackgroundScore.png')

    # Buttons
    buttonBack = ButtonImg((578, 450), 'Project - Balloon Pop/ButtonBack.png',
                           pathSoundClick='Sounds/click.mp3',
                           pathSoundHover='Sounds/hover.mp3',
                           scale=0.5)

    # Load Music
    pygame.mixer.pre_init()
    pygame.mixer.music.load("../Project - Balloon Pop/BackgroundMusicGame.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    # Get all Balloon paths
    pathBalloonFolder = "Project - Balloon Pop/BalloonsA/"
    pathListBalloons = os.listdir(pathBalloonFolder)
    print(pathListBalloons)

    # Balloon Generator
    def generateBalloon():
        # Random X location for generation
        randomBallonPath = pathListBalloons[random.randint(0, len(pathListBalloons) - 1)]
        x = random.randint(100, width - 100)  # Fixed the width reference
        y = height
        randomScale = round(random.uniform(0.3, 0.7), 2)
        balloons.append(Balloon((x, y),
                                path=os.path.join(pathBalloonFolder, randomBallonPath),
                                grid=(3, 4), scale=randomScale, speed=speed,
                                pathSoundPop="Project - Balloon Pop/Pop.wav"))

    # Main loop
    start = True
    while start:
        # Get Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    SceneManager.OpenScene("Menu")

        # Check if time is up
        timeRemaining = totalTime - (time.time() - startTime)

        if timeRemaining < 0:
            window.blit(imgScore, (0, 0))
            font = pygame.font.Font("../Marcellus-Regular.ttf", 100)
            textScore = font.render(f'Score: {score}', True, (255, 50, 50))
            textScoreRect = textScore.get_rect(center=(width / 2, height / 2))
            window.blit(textScore, textScoreRect)
            buttonBack.draw(window)
            if buttonBack.state == 'clicked':
                pygame.mixer.music.stop()
                SceneManager.OpenScene('Menu')

        else:
            # Apply Logic
            # OpenCV
            success, img = cap.read()
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = pose.process(imgRGB)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark

                # Extract hand landmarks (assuming index 0 is the left hand)

                nose_landmark = landmarks[0]  # Replace 0 with appropriate index for hand landmarks

                # Convert hand landmark coordinates to pixel coordinates
                h, w, _ = img.shape
                x, y = int(nose_landmark.x * w), int(nose_landmark.y * h)

                pygame.draw.circle(window, (0, 200, 0), (x, y), 20)
                pygame.draw.circle(window, (200, 200, 200), (x, y), 16)

            imgRGB = np.rot90(imgRGB)
            frame = pygame.surfarray.make_surface(imgRGB).convert()
            frame = pygame.transform.flip(frame, True, False)
            window.blit(frame, (0, 0))
            #x, y = 0, 0

            # Update balloon logic
            for i, balloon in enumerate(balloons):
                if balloon:
                    ballonScore = balloon.checkPop(x, y)
                    if ballonScore:
                        score += ballonScore // 10
                        balloons[i] = False
                    balloon.draw(window)

            if time.time() - generatorStartTime > generatorDelay:
                generatorDelay = random.uniform(0.3, 0.8)
                generateBalloon()
                generatorStartTime = time.time()
                speed += 1

            font = pygame.font.Font("../Marcellus-Regular.ttf", 50)
            textScore = font.render(f'Score: {score}', True, (255, 255, 255))
            textTime = font.render(f'Time: {int(timeRemaining)}', True, (255, 255, 255))
            pygame.draw.rect(window, (200, 0, 200), (10, 10, 300, 70), border_radius=20)
            pygame.draw.rect(window, (200, 0, 200), (950, 10, 300, 70), border_radius=20)
            window.blit(textScore, (40, 13))
            window.blit(textTime, (1000, 13))

        # Update Display
        pygame.display.update()
        # Set FPS
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    Game()
