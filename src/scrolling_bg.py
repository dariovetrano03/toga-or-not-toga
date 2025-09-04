import pygame
import math
import os

pygame.init()

clock = pygame.time.Clock()
FPS = 60

script_dir = os.path.dirname(os.path.abspath(__file__))  # script folder
parent_dir = os.path.dirname(script_dir) 

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 768 # = bg_height

#create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Scroll")
  

#load image
bg = pygame.image.load(f"{parent_dir}/sprite/background.png").convert()
bg_width = bg.get_width()
bg_rect = bg.get_rect()


#define game variables
scroll = 0
tiles = math.ceil(SCREEN_WIDTH  / bg_width) + 1

#game loop
run = True
while run:

  clock.tick(FPS)

  #draw scrolling background
  for i in range(0, tiles):
    screen.blit(bg, (i * bg_width - scroll, 0))
    bg_rect.x = i * bg_width - scroll

  #scroll background speed
  scroll += 5

  #reset scroll
  if scroll > bg_width:
    scroll = 0

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()

pygame.quit()