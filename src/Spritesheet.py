import pygame

GREY = (50, 50, 50 )

class Spritesheet():
    def __init__(self, image):
        self.sheet = image
    
    def setup(self, anim_list, anim_steps):

        # Just for the correct initialization of the 'aircraft_anim_list':
        count1 = 0          # Scans through the different flame intesities for a given nozzle opening
        count2 = 0          # Scans through the different nozzle openings

        for set_animation in anim_steps:   
            temp_set_img_list = []
            for animation in set_animation:
                temp_img_list = []
                for _ in range(animation):
                    temp_img_list.append(self.get_image(count1, 64, 64, 6, GREY))
                    count1 += 1
                temp_set_img_list.append(temp_img_list)
                count2 += 1
            anim_list.append(temp_set_img_list)
        return anim_list


    def get_image(self, frame, width, height, scale, color):
        image = pygame.Surface((width, height)).convert_alpha()
        image.fill(GREY)
        image.blit(self.sheet, (0, 0), ((frame * width, 0, width, height)))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)

        return image
    