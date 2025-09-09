import pygame

class TextBox():
    def __init__(self, path_to_png, scale = 1):
        img_pygame = pygame.image.load(path_to_png).convert_alpha()
        self.pygame_image = img_pygame