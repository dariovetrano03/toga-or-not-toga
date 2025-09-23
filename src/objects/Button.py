import pygame

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def draw(self, screen, anim_count):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()
        
        # check mouse over and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == True:
                action = True       

        screen.blit(self.image, (self.rect.x + anim_count, self.rect.y))
        return action

