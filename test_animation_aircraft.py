import pygame
import src.Spritesheet as spritesheet
 
pygame.init()

pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Nome joystick:", joystick.get_name())
print("Numero assi:", joystick.get_numaxes())
print("Numero pulsanti:", joystick.get_numbuttons())


SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Test Engine")

clock = pygame.time.Clock()
FPS = 60

BG = (0, 181, 226)
BLACK = (0, 0, 0)
GREY = (50, 50, 50)

sprite_sheet_png = pygame.image.load('./sprite/spreadsheet_aircraft.png').convert_alpha()
sprite_sheet = spritesheet.Spritesheet(sprite_sheet_png) 

# class Aircraft(pygame.sprite.Sprite):
#     def __init__(self, col, x, y):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface(())

aircraft_anim_list = []
aircraft_anim_steps = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]

last_update = pygame.time.get_ticks()
animation_cooldown = 100

nozzle_idx = 1
throttle_idx = 1

frame = 0

count1 = 0
count2 = 0

for set_animation in aircraft_anim_steps:
    temp_set_img_list = []
    for animation in set_animation:
        temp_img_list = []
        for _ in range(animation):
            temp_img_list.append(sprite_sheet.get_image(count1, 64, 64, 6, GREY))
            count1 += 1
        temp_set_img_list.append(temp_img_list)
        count2 += 1
    aircraft_anim_list.append(temp_set_img_list)

running = True
while running:
    # clock.tick(60)

    x_js = joystick.get_axis(0)
    y_js = joystick.get_axis(1)

    screen.fill(BG)
    
    # update animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = pygame.time.get_ticks()
        if frame >= len(aircraft_anim_list[nozzle_idx]):
            frame = 0

    # # show frame image
    screen.blit(aircraft_anim_list[nozzle_idx][throttle_idx][frame], (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_DOWN) and throttle_idx > 0:
                throttle_idx -= 1
                frame = 0
            if (event.key == pygame.K_UP) and throttle_idx < len(aircraft_anim_list[nozzle_idx]) - 1:
                throttle_idx += 1
                frame = 0
            if (event.key == pygame.K_LEFT) and nozzle_idx > 0:
                nozzle_idx -= 1
                frame = 0

            if (event.key == pygame.K_RIGHT) and nozzle_idx < len(aircraft_anim_list[nozzle_idx]) - 1:
                nozzle_idx += 1
                frame = 0

        elif event.type == pygame.JOYAXISMOTION:
            print(x_js)
            if abs(y_js) <= 0.400:
                throttle_idx = 1 
            if abs(x_js) <= 0.400:
                nozzle_idx = 1
            if (y_js >= 0.400) and throttle_idx > 0:
                throttle_idx -= 1
                frame = 0
            if (y_js < -0.400) and throttle_idx < len(aircraft_anim_list[nozzle_idx]) - 1:
                throttle_idx += 1
                frame = 0
            if (x_js < -0.400) and nozzle_idx > 0:
                nozzle_idx -= 1
                frame = 0

            if (x_js > 0.400) and nozzle_idx < len(aircraft_anim_list[nozzle_idx]) - 1:
                nozzle_idx += 1
                frame = 0

    pygame.display.update()



pygame.quit()
