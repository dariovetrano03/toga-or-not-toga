import pygame
from src.Spritesheet import Spritesheet
from src.Button import Button
import math
from src.functions import plot_compressor_map

pygame.init()
pygame.joystick.init()
font = pygame.font.Font("./font/Press_Start_2P/PressStart2P-Regular.ttf", 24) 


try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    joystick_flag = True
except pygame.error:
    joystick_flag = False
    print("No joystick detected. Keyboard mode only.")


SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("To GA or not to GA?")

clock = pygame.time.Clock()
FPS = 60

BG = (0, 181, 226) # Blue Sky RGB color
BLACK = (0, 0, 0)  
GREY = (50, 50, 50) # Grey RGB color selected for the pygame.Surface bg. Choosing black poses issues with the sprite outline being deleted.

""" AIRCRAFT RUNWAY BACKGROUND """

#load image
bg = pygame.image.load(f"./sprite/background.png").convert()
bg_width = bg.get_width()
bg_rect = bg.get_rect()


#define game variables
scroll = 0
tiles = math.ceil(SCREEN_WIDTH  / bg_width) + 1


""" INSTRUCTIONS LEGEND SETUP """
legend_img = pygame.image.load('./sprite/instructions.png').convert_alpha()

""" BUTTON SETUP """
start_button_img = pygame.image.load('./sprite/start_button.png').convert_alpha()
start_button = Button(SCREEN_WIDTH//1.5, 50, start_button_img, 0.25)
anim_btn_count = 0

""" AIRCRAFT SETUP """
spritesheet_wheels_up_png = pygame.image.load('./sprite/spreadsheet_aircraft_wheels_up.png').convert_alpha() 
spritesheet_wheels_up = Spritesheet(spritesheet_wheels_up_png) 

spritesheet_wheels_down_png = pygame.image.load('./sprite/spreadsheet_aircraft_wheels_down.png').convert_alpha() 
spritesheet_wheels_down = Spritesheet(spritesheet_wheels_down_png) 

spritesheet_wheels_down_flap_down_png = pygame.image.load('./sprite/spreadsheet_aircraft_wheels_down_flap.png').convert_alpha() 
spritesheet_wheels_down_flap_down = Spritesheet(spritesheet_wheels_down_flap_down_png) 

spritesheet_wheels_up_flap_down_png = pygame.image.load('./sprite/spreadsheet_aircraft_wheels_up_flap.png').convert_alpha() 
spritesheet_wheels_up_flap_down = Spritesheet(spritesheet_wheels_up_flap_down_png) 



aircraft_anim_list_wheels_up = []
aircraft_anim_steps_wheels_up = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] # Each of the Idle / Cruiste / TOGA flame lengths has Narrow / Normal / Wide Nozzle exit. 
                                                        # Once that the [nozzle_idx][throttle_idx] combination is chosen, the Flame animation 
                                                        # effect is achieved through three subsequent frames (3 * 3 * 3 = 27 sprites with size 64x64, 
                                                        # in the spritesheet, arranged on a 1x27 table, cfr. with 'sprite/spreadsheet_aircraft.png')
aircraft_anim_list_wheels_up = spritesheet_wheels_up.setup(aircraft_anim_list_wheels_up, aircraft_anim_steps_wheels_up, 6)


aircraft_anim_list_wheels_down = []
aircraft_anim_steps_wheels_down = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_down = spritesheet_wheels_down.setup(aircraft_anim_list_wheels_down, aircraft_anim_steps_wheels_down, 6)

aircraft_anim_list_wheels_down_flap_down = []
aircraft_anim_steps_wheels_down_flap_down = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_down_flap_down = spritesheet_wheels_down_flap_down.setup(aircraft_anim_list_wheels_down_flap_down, aircraft_anim_steps_wheels_down_flap_down, 6)

aircraft_anim_list_wheels_up_flap_down = []
aircraft_anim_steps_wheels_up_flap_down = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_up_flap_down = spritesheet_wheels_up_flap_down.setup(aircraft_anim_list_wheels_up_flap_down, aircraft_anim_steps_wheels_up_flap_down, 6)


aircraft_anim_list_wheels_up_scaled = []
aircraft_anim_steps_wheels_up_scaled = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_up_scaled = spritesheet_wheels_up.setup(aircraft_anim_list_wheels_up_scaled, aircraft_anim_steps_wheels_up_scaled, 3)


aircraft_anim_list_wheels_down_scaled = []
aircraft_anim_steps_wheels_down_scaled = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_down_scaled = spritesheet_wheels_down.setup(aircraft_anim_list_wheels_down_scaled, aircraft_anim_steps_wheels_down_scaled, 3)

aircraft_anim_list_wheels_down_flap_down_scaled = []
aircraft_anim_steps_wheels_down_flap_down_scaled = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_down_flap_down_scaled = spritesheet_wheels_down_flap_down.setup(aircraft_anim_list_wheels_down_flap_down_scaled, aircraft_anim_steps_wheels_down_flap_down_scaled, 3)

aircraft_anim_list_wheels_up_flap_down_scaled = []
aircraft_anim_steps_wheels_up_flap_down_scaled = [[3, 3, 3], [3, 3, 3], [3, 3, 3]] 
aircraft_anim_list_wheels_up_flap_down_scaled = spritesheet_wheels_up_flap_down.setup(aircraft_anim_list_wheels_up_flap_down_scaled, aircraft_anim_steps_wheels_up_flap_down_scaled, 3)


aircraft_anim_list = []

# Current animation
aircraft_anim_list = aircraft_anim_list_wheels_up

last_update_flame = pygame.time.get_ticks()
animation_flame = 300

nozzle_dof = 1.1      # Effective DOF controlling the working line
throttle_dof = 92    # Effective DOF controlling the working point

nozzle_idx = 1     # Animation selector for the nozzle opening
throttle_idx = 1    # Animation selector fot the flame intensity

frame = 0

stall = False # If the margin between the working line and the surge line becomes <= 0 then stall = True 


""" TEXT BLINKING INSTRUCTIONS """
blink_time = 1000  # time interval for blinking text
BLINK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(BLINK_EVENT, blink_time)


start_text = font.render("Press START to play:", True, (255, 255, 255))

last_update_text = pygame.time.get_ticks()

L_pressed = False
F_pressed = False

waiting_flag = True

show_text = True

running = True

instructions_text = "↔ Nozzle exit area\n⇅ Throttle\nL Landing Gear\nF Flap"


while running:
    clock.tick(60)
    if joystick_flag:
        x_js = joystick.get_axis(0)
        y_js = joystick.get_axis(1)

    screen.fill(BG)

    for i in range(0, tiles):
        screen.blit(bg, (i * bg_width - scroll, 0))
        bg_rect.x = i * bg_width - scroll

    #scroll background speed
    scroll += (throttle_dof - 50) # throttle dof varies between 84 and 100, but i dont want the bg to stop when throttle_dof = 84

    #reset scroll
    if scroll > bg_width:
        scroll = 0
    
    # Should the animation be updated if enough time has elapsed?
    current_time = pygame.time.get_ticks()
    if current_time - last_update_flame >= animation_flame:
        frame += 1
        last_update_flame = pygame.time.get_ticks()
        if frame >= len(aircraft_anim_list[nozzle_idx]):
            frame = 0
        
        if anim_btn_count // 2 == 0:
            anim_btn_count += 1
        else:
            anim_btn_count -= 1
            
    # Show the aircraft (either if it's updated or not)
    screen.blit(aircraft_anim_list[nozzle_idx][throttle_idx][frame], (SCREEN_WIDTH//9, SCREEN_HEIGHT//3))
    screen.blit(legend_img, (0, 0))
    compressor_map, margin = plot_compressor_map(throttle_dof, nozzle_dof, stall, SCREEN_WIDTH//2.5, SCREEN_HEIGHT//1.5)
    
    screen.blit(compressor_map, (SCREEN_WIDTH//1.75, SCREEN_HEIGHT//3.5))
    
    if waiting_flag:
        if start_button.draw(screen, anim_btn_count): # the draw method returns True when the button is pressed
            pygame.display.flip()
            waiting_flag = False
            show_text = False

            if F_pressed and L_pressed:
                aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
            else:
                if F_pressed and not L_pressed:
                    aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                elif L_pressed and not F_pressed:
                    aircraft_anim_list = aircraft_anim_list_wheels_down_scaled
                else:
                    aircraft_anim_list = aircraft_anim_list_wheels_up_scaled
                

    if show_text:
        screen.blit(start_text, (250, 100)) 


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == BLINK_EVENT and waiting_flag:
            show_text = not show_text  
            
        # You can control either by keyboard...
        elif event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_DOWN):
                throttle_idx = max(0, throttle_idx - 1)
                throttle_dof = max(84, throttle_dof - 1)

                frame = 0

            if (event.key == pygame.K_UP):
                throttle_idx = min(len(aircraft_anim_list[nozzle_idx]) - 1, throttle_idx + 1)
                throttle_dof = min(100, throttle_dof + 1)

                frame = 0

            if (event.key == pygame.K_LEFT):
                nozzle_idx = max(0, nozzle_idx - 1)
                nozzle_dof = max(0.9, nozzle_dof - 0.05)

                frame = 0

            if (event.key == pygame.K_RIGHT):
                nozzle_idx = min(len(aircraft_anim_list[nozzle_idx]) - 1, nozzle_idx + 1)
                nozzle_dof = min(1.3, nozzle_dof + 0.05)

                frame = 0

            if (event.key == pygame.K_l):
                L_pressed = not L_pressed

                if waiting_flag:
                    if F_pressed:
                        if L_pressed:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down
                    else:
                        aircraft_anim_list = aircraft_anim_list_wheels_down
            
                else:
                    if F_pressed and not waiting_flag:
                        if L_pressed:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                    else:
                        aircraft_anim_list = aircraft_anim_list_wheels_down_scaled

            if (event.key == pygame.K_f) :
                F_pressed = not F_pressed

                if waiting_flag:
                    if L_pressed:
                        if F_pressed:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_down
                    else:
                        aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down
                
                else:
                    if L_pressed:
                        if L_pressed:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_scaled
                    else:
                        aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled

        if not F_pressed and not L_pressed:
            if waiting_flag:
                aircraft_anim_list = aircraft_anim_list_wheels_up
            else:
                aircraft_anim_list = aircraft_anim_list_wheels_up_scaled
                
           

        # TODO Add the DOF controls also in the Joystick mode
        elif event.type == pygame.JOYAXISMOTION and joystick_flag:
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
