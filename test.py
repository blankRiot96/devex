import math
import sys

import pygame

# Initialize pygame
pygame.init()

# Set up the window
window_width = 640
window_height = 480
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Spiral Entities")

# Set up the clock
clock = pygame.time.Clock()


class Entity:
    def __init__(self, angle):
        self.angle = angle
        self.color = (255, 0, 0)
        self.size = 10

    def update(self, mouse_position, radius):
        self.angle += 0.02
        self.x = mouse_position[0] + radius * math.cos(self.angle)
        self.y = mouse_position[1] + radius * math.sin(self.angle)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


# Set up the entities
num_entities = 8
entities = []
for i in range(num_entities):
    angle = 2 * math.pi * i / num_entities
    entities.append(Entity(angle))
radius = 150

# Start the game loop
while True:
    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the position of the mouse
    mouse_position = pygame.mouse.get_pos()

    for event in events:
        if event.type == pygame.MOUSEWHEEL:
            radius += event.precise_y * 20

    # Update the entities
    for entity in entities:
        entity.update(mouse_position, radius)

    # Clear the screen
    window.fill((255, 255, 255))

    # Draw the entities
    for entity in entities:
        entity.draw(window)

    # Update the display
    pygame.display.update()

    # Wait for the next frame
    clock.tick(60)  # limit the frame rate to 60 FPS
