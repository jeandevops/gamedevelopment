import pygame
from pygame.locals import QUIT
from sys import exit
from constants import BLACK

pygame.init()
pygame.display.set_caption("World of Tiles")

width, height = 800, 600

screen = pygame.display.set_mode((width, height))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
    
    screen.fill(BLACK)
    pygame.display.update()