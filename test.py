import pygame

screen = pygame.display.set_mode((600, 450))
clock = pygame.time.Clock()


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()
    clock.tick(60)
