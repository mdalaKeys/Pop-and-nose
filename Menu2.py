import pygame
import csv
import os
from Button import ButtonImg
import SceneManager

def get_sorted_scores():
    if not os.path.isfile('scores.csv'):
        return []
    with open('scores.csv', mode='r') as file:
        reader = csv.DictReader(file)
        scores = [row for row in reader]
        headers = [header.strip() for header in reader.fieldnames]
        if 'Score' not in headers:
            raise KeyError("The column 'Score' is missing from the CSV header.")
        sorted_scores = sorted(scores, key=lambda x: int(x['Score']), reverse=True)
    return sorted_scores

def display_scores(window, width, height):
    scores = get_sorted_scores()
    title_font = pygame.font.Font('Marcellus-Regular.ttf', 50)  # Title font
    header_font = pygame.font.Font('Marcellus-Regular.ttf', 30)  # Header font
    font = pygame.font.Font('Marcellus-Regular.ttf', 24)  # Score font

    # Define table parameters
    table_x, table_y = width // 2 - 200, 100
    table_width = 400
    header_height = 60
    row_height = 50

    # Calculate table height based on the number of scores
    num_scores = len(scores)
    table_height = header_height + num_scores * row_height + 20  # Extra space for padding

    # Draw table
    pygame.draw.rect(window, (128, 128, 128), (table_x, table_y, table_width, table_height), 2)
    pygame.draw.rect(window, (128, 128, 128), (table_x, table_y, table_width, header_height), 2)
    for i in range(1, num_scores + 1):  # Drawing horizontal lines
        pygame.draw.line(window, (128, 128, 128), (table_x, table_y + header_height + i * row_height), (table_x + table_width, table_y + header_height + i * row_height), 2)

    # Draw table headers
    headers = ['Rank', 'Username', 'Score']
    header_widths = [100, 200, 100]
    x_offset = table_x + 10
    for i, header in enumerate(headers):
        text = header_font.render(header, True, (128, 128, 128))
        window.blit(text, (x_offset, table_y + 10))
        x_offset += header_widths[i]

    # Draw table rows
    y_offset = table_y + header_height + 10
    for i, entry in enumerate(scores[:10]):  # Display top 10 scores
        rank_text = font.render(f"{i + 1}", True, (255, 255, 255))
        username_text = font.render(entry['Username'], True, (255, 255, 255))
        score_text = font.render(entry['Score'], True, (255, 255, 255))
        window.blit(rank_text, (table_x + 20, y_offset))
        window.blit(username_text, (table_x + 120, y_offset))
        window.blit(score_text, (table_x + 320, y_offset))
        y_offset += row_height

def Menu():
    pygame.init()

    # Window setup
    width, height = 1280, 720
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Menu")

    # Load background image once
    background_img = pygame.image.load('Project - Balloon Pop/hd2.jpg').convert()

    # Create ButtonImg instance once
    buttonBack = ButtonImg((width // 2.2, height - 100), 'Project - Balloon Pop/ButtonBack.png',
                           pathSoundClick='Sounds/click.mp3',
                           pathSoundHover='Sounds/hover.mp3',
                           scale=0.5)

    running = True
    while running:
        # Blit the background image
        window.blit(background_img, (0, 0))

        # Display Scores and Menu
        display_scores(window, width, height)

        # Draw the button after displaying scores
        buttonBack.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    SceneManager.OpenScene("Game")  # Transition to the Game scene
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for back button click
                if buttonBack.collidepoint(event.pos):
                    SceneManager.OpenScene("Game")  # Transition to the Game scene
                    running = False  # Exit the loop to transition to the game

        pygame.display.update()

if __name__ == "__main__":
    Menu()
