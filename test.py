import pygame

screen = pygame.display.set_mode((600, 450))
clock = pygame.time.Clock()

player = pygame.Surface((50, 50))
player.fill("red")
player_rect = player.get_rect(center=(200, 200))
pos = pygame.Vector2(player_rect.center)

background = pygame.Surface((100, 100))
background.fill("purple")

bloom = pygame.image.load("assets/light.png").convert_alpha()
bloom_rect = bloom.get_rect(center=player_rect.center)
overlay = pygame.Surface(screen.get_size())


while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        pos.x += 10
    if keys[pygame.K_LEFT]:
        pos.x -= 10
    if keys[pygame.K_UP]:
        pos.y -= 10
    if keys[pygame.K_DOWN]:
        pos.y += 10

    player_rect.center = pos
    bloom_rect.center = pos
    screen.fill("black")
    screen.blit(background, (200, 1000))
    screen.blit(player, player_rect)

    overlay.fill("black")
    overlay.blit(bloom, bloom_rect)
    screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

    pygame.display.update()
    clock.tick(60)
