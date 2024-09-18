import os
import random
import pygame
import SceneManager
import csv
import cv2
import numpy as np
import time
import mediapipe as mp
from Button import ButtonImg

class Balloon:
    def __init__(self, pos, path, scale=1, grid=(2, 4),
                 animationFrames=None, speedAnimation=1, speed=3, pathSoundPop=None):
        img = pygame.image.load(path).convert_alpha()
        width, height = img.get_size()
        img = pygame.transform.smoothscale(img, (int(width * scale), int(height * scale)))
        width, height = img.get_size()

        if animationFrames is None:
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
        if not self.isAnimating:
            self.rectImg.y -= self.speed
        window.blit(self.img, self.rectImg)

    def checkPop(self, x, y):
        if self.rectImg.collidepoint(x, y) and not self.isAnimating:
            self.isAnimating = True
            if self.pathSoundPop:
                self.soundPop.play()

        if self.isAnimating:
            if self.animationCount != len(self.imgList) - 1:
                self.animationCount += 1
                self.img = self.imgList[self.animationCount]
            else:
                self.pop = True

        if self.pop:
            return self.rectImg.y
        else:
            return None

def update_csv(username, score):
    file_exists = os.path.isfile('scores.csv')
    with open('scores.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Username', 'Score'])
        writer.writerow([username, score])

def username_input(window, width, height):
    # Initialize video capture (replace 'video.mp4' with your video path)
    video_path = "Project - Balloon Pop/mp44.mp4"
    cap = cv2.VideoCapture(video_path)

    pygame.font.init()

    # Set up font and input box parameters
    font = pygame.font.Font(None, 74)
    input_box_width = 300
    input_box_height = 75
    input_box = pygame.Rect(
        (width - input_box_width) // 2 + 290,  # Center horizontally
        (height - input_box_height) // 2 + 130,  # Move it down by 50 pixels
        input_box_width,
        input_box_height
    )

    # Colors for inactive/active input box
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    active = False
    text = ''
    clock = pygame.time.Clock()

    # Welcome text rendering
    welcome_font = pygame.font.Font('Marcellus-Regular.ttf', 50)
    welcome_text1 = welcome_font.render('Enter your name', True, (255, 0, 0))
    welcome_text1_rect = welcome_text1.get_rect(center=(width // 1.38, (height // 1.47) - 100))

    welcome_text2 = welcome_font.render('Welcome to Pop and Nose', True, (255, 0, 0))
    welcome_text2_rect = welcome_text2.get_rect(center=(width // 1.38, (height // 1.5) - 150))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle active status based on input box click
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Read video frame-by-frame
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            continue

        # Rotate the frame 90 degrees clockwise
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Convert the frame to RGB (from BGR, which OpenCV uses)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a Pygame surface
        frame_surface = pygame.surfarray.make_surface(frame)
        frame_surface = pygame.transform.scale(frame_surface, (width, height))

        # Draw the video frame and text
        window.blit(frame_surface, (0, 0))
        window.blit(welcome_text1, welcome_text1_rect)
        window.blit(welcome_text2, welcome_text2_rect)

        # Render the text input
        txt_surface = font.render(text, True, color)
        input_box.w = max(input_box_width, txt_surface.get_width() + 10)

        # Draw the input box and text
        window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(window, color, input_box, 2)

        # Update the screen once per frame
        pygame.display.flip()
        clock.tick(30)

    # Make sure to release the video capture once you're done
    cap.release()


def Game():
    pygame.init()
    pygame.event.clear()
    global width, height
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pop And Nose")
    fps = 30
    clock = pygame.time.Clock()
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    pygame.mixer.pre_init()
    pygame.mixer.music.load("Project - Balloon Pop/DreamLand.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    pathBalloonFolder = "Project - Balloon Pop/BalloonsA/"
    pathListBalloons = os.listdir(pathBalloonFolder)

    def generateBalloon():
        randomBallonPath = pathListBalloons[random.randint(0, len(pathListBalloons) - 1)]
        x = random.randint(100, width - 100)
        y = height
        randomScale = round(random.uniform(0.3, 0.7), 2)
        balloons.append(Balloon((x, y),
                                path=os.path.join(pathBalloonFolder, randomBallonPath),
                                grid=(3, 4), scale=randomScale, speed=speed,
                                pathSoundPop="Project - Balloon Pop/Pop.wav"))

    try:
        # Get the username before starting the game and countdown
        username = username_input(window, width, height)

        balloons = []
        startTime = time.time()  # Start the timer after getting username
        generatorStartTime = time.time()
        generatorDelay = 1
        speed = 5
        score = 0
        totalTime = 30

        imgScore = pygame.image.load('Project - Balloon Pop/hd.png')
        buttonBack = ButtonImg((578, 500), 'Project - Balloon Pop/ButtonBack.png',
                               pathSoundClick='Sounds/click.mp3',
                               pathSoundHover='Sounds/hover.mp3',
                               scale=0.5)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        SceneManager.OpenScene("Menu2")

            timeRemaining = totalTime - (time.time() - startTime)

            if timeRemaining < 0:
                window.blit(imgScore, (0, 0))
                font = pygame.font.Font("Marcellus-Regular.ttf", 70)
                textScore = font.render(f'Final Score: {score}', True, (255, 255, 255))
                textScoreRect = textScore.get_rect(center=(width / 1.3, height / 1.3))
                window.blit(textScore, textScoreRect)
                buttonBack.draw(window)
                if buttonBack.state == 'clicked':
                    update_csv(username, score)
                    pygame.mixer.music.stop()
                    SceneManager.OpenScene("Menu2")

            else:
                success, img = cap.read()
                img = cv2.flip(img, 1)
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = pose.process(imgRGB)

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    landmarks = results.pose_landmarks.landmark
                    nose_landmark = landmarks[0]
                    h, w, _ = img.shape
                    x, y = int(nose_landmark.x * w), int(nose_landmark.y * h)
                    pygame.draw.circle(window, (0, 200, 0), (x, y), 20)
                    pygame.draw.circle(window, (200, 200, 200), (x, y), 16)

                imgRGB = np.rot90(imgRGB)
                frame = pygame.surfarray.make_surface(imgRGB).convert()
                frame = pygame.transform.flip(frame, True, False)
                window.blit(frame, (0, 0))

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

                font = pygame.font.Font("Marcellus-Regular.ttf", 50)
                textScore = font.render(f'Score: {score}', True, (255, 255, 255))
                textTime = font.render(f'Time: {int(timeRemaining)}', True, (255, 255, 255))
                pygame.draw.rect(window, (0, 0, 200), (10, 10, 300, 70), border_radius=20)
                pygame.draw.rect(window, (0, 0, 200), (950, 10, 300, 70), border_radius=20)
                window.blit(textScore, (40, 13))
                window.blit(textTime, (1000, 13))

            pygame.display.update()
            clock.tick(fps)

    finally:
        pygame.quit()


if __name__ == "__main__":
    Game()

