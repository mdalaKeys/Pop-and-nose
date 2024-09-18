# Import
import os
import random
import SceneManager
import pygame
import csv
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
        if not self.isAnimating:
            self.rectImg.y -= self.speed
        window.blit(self.img, self.rectImg)

    def checkPop(self, x, y):
        # Check for the hit
        if self.rectImg.collidepoint(x, y) and not self.isAnimating:
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

def update_csv(username, score):
    file_exists = os.path.isfile('../scores.csv')
    with open('../scores.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Username', 'Score'])  # Write header if file does not exist
        writer.writerow([username, score])

def get_sorted_scores():
    if not os.path.isfile('../scores.csv'):
        return []
    with open('../scores.csv', mode='r') as file:
        reader = csv.DictReader(file)
        scores = [row for row in reader]
        # Trim spaces from header
        headers = [header.strip() for header in reader.fieldnames]
        # Print headers to verify
        print("CSV Headers:", headers)
        # Ensure correct headers are used
        if 'Score' not in headers:
            raise KeyError("The column 'Score' is missing from the CSV header.")
        # Sort by score in descending order
        sorted_scores = sorted(scores, key=lambda x: int(x['Score']), reverse=True)
    return sorted_scores


def display_game_over(window, score, username):
    window.fill((0, 0, 0))
    font = pygame.font.Font(None, 100)
    text = font.render(f'Game Over! Your Score: {score}', True, (255, 0, 0))
    text_rect = text.get_rect(center=(width / 2, height / 2 - 50))
    window.blit(text, text_rect)

    # Update CSV (only once)
    update_csv(username, score)

    # Display leaderboard
    font_small = pygame.font.Font(None, 50)
    y_offset = height / 2 + 50
    sorted_scores = get_sorted_scores()
    if sorted_scores:
        for i, entry in enumerate(sorted_scores[:10]):  # Display top 10 scores
            text = font_small.render(f"{i + 1}. {entry.get('Username', 'Unknown')}: {entry.get('Score', '0')}", True, (255, 255, 255))
            window.blit(text, (width / 2 - 100, y_offset))
            y_offset += 30
    else:
        no_scores_text = font_small.render("No scores available.", True, (255, 255, 255))
        window.blit(no_scores_text, (width / 2 - 100, y_offset))

    class Button:
        def __init__(self, pos, text, font_size=50, color=(0, 255, 0), bg_color=(0, 0, 0)):
            self.font = pygame.font.Font(None, font_size)
            self.text = text
            self.color = color
            self.bg_color = bg_color
            self.pos = pos
            self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
            self.clicked = False

        def draw(self, window):
            pygame.draw.rect(window, self.bg_color, self.rect)
            text_surface = self.font.render(self.text, True, self.color)
            window.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
            pygame.draw.rect(window, self.color, self.rect, 2)

        def is_clicked(self, mouse_pos):
            return self.rect.collidepoint(mouse_pos)

    # Create and display the restart button
    restart_button = Button((width / 2 - 100, height / 2 + 150), "Restart Game")
    restart_button.draw(window)

    pygame.display.update()

    # Event loop to handle button clicks
    button_clicked = False
    while not button_clicked:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos):
                    button_clicked = True
                    return True  # Return True to signal that the game should restart

def username_input(window, width, height):
    pygame.font.init()
    font = pygame.font.Font(None, 74)
    input_box_width = 300
    input_box_height = 75
    input_box = pygame.Rect((width - input_box_width) // 2, (height - input_box_height) // 2, input_box_width, input_box_height)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    clock = pygame.time.Clock()

    # Welcome message
    welcome_font = pygame.font.Font(None, 50)
    welcome_text = welcome_font.render('Enter your name:', True, (255, 255, 255))
    welcome_text_rect = welcome_text.get_rect(center=(width // 2, (height // 2) - 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        window.fill((30, 30, 30))
        window.blit(welcome_text, welcome_text_rect)

        txt_surface = font.render(text, True, color)
        width = max(input_box_width, txt_surface.get_width() + 10)
        input_box.w = width
        window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(window, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

def Game():
    # Initialize
    pygame.init()
    pygame.event.clear()

    # Create Window/Display
    global width, height
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pop And Nose")

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
    username = username_input(window, width, height)  # Pass window to the username_input function
    while start:
        # Get Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    SceneManager.OpenScene("PoseEstGameUpdate")

        # Check if time is up
        timeRemaining = totalTime - (time.time() - startTime)

        if timeRemaining < 0:
            window.blit(imgScore, (0, 0))
            font = pygame.font.Font("../Marcellus-Regular.ttf", 70)
            textScore = font.render(f'Final Score: {score}', True, (255, 255, 255))
            textScoreRect = textScore.get_rect(center=(width / 2, height / 2))
            window.blit(textScore, textScoreRect)
            buttonBack.draw(window)
            if buttonBack.state == 'clicked':
                pygame.mixer.music.stop()
                SceneManager.OpenScene("PoseEstGameUpdate")
            display_game_over(window, score, username)

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
