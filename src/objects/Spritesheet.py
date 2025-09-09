import pygame

GREY = (50, 50, 50)

class AircraftSpritesheet():
    def __init__(self, path_to_png, anim_steps, scale = 1):

        spritesheet_png =  pygame.image.load(path_to_png).convert_alpha()

        self.pygame_image = spritesheet_png 

        anim_list = []

        anim_list = self.setup(anim_list, anim_steps, scale)

        self.anim_list = anim_list
    
    def setup(self, anim_list, anim_steps, scale):
        """
        Set up a spritesheet for an animated character or object.

        A spritesheet is an image consisting of a single row of adjacent sprites. 
        By default, each sprite is a 64x64 pixel square. Spritesheets can contain 
        multiple variations for the same character or object. 

        For example, a spritesheet for a running character with 2 alternating frames 
        and 3 different running styles, with or without a hat, would be a row of 
        1x12 sprites (image size W x H = 12*64 x 64). The mapping of which sprites 
        correspond to which set of options (e.g., running style 2, without a hat) 
        should be provided via `anim_list`.

        Parameters
        ----------
        anim_list : list of list of int
            A nested list specifying the sprite indices for each variation. 
            Each sublist corresponds to a character variation (e.g., with or without a hat), 
            and each element of a sublist corresponds to a specific animation style.
            Example: [[2, 2, 2], [2, 2, 2]].
        anim_steps : int
            Number of frames per animation step.
        scale : float
            Scaling factor to apply to each sprite.
        """
        frame_abs_idx = 0

        for set_animation in anim_steps: 
            
            temp_set_anims = [] # temporary set of anims

            for animation_len in set_animation:
                
                temp_frame_list = [] # temporary list of frames

                for frame_idx in range(animation_len):
                    temp_frame_list.append(self.get_image(frame_abs_idx, 64, 64, scale, GREY))
                    frame_abs_idx += 1
                temp_set_anims.append(temp_frame_list)

            anim_list.append(temp_set_anims)

        return anim_list


    def get_image(self, frame, width, height, scale, color):
            image = pygame.Surface((width, height)).convert_alpha()
            image.fill(GREY)
            image.blit(self.pygame_image, (0, 0), (frame * width, 0, width, height))
            image = pygame.transform.scale(image, (width * scale, height * scale))
            image.set_colorkey(color)

            return image
        