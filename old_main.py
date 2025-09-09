import pygame
from src.functions.game_functions import plot_compressor_map
from src.objects.Spritesheet import AircraftSpritesheet
from src.objects.Button import Button
import math

pygame.init()
pygame.joystick.init()
font = pygame.font.Font("./font/Press_Start_2P/PressStart2P-Regular.ttf", 24) 


# try:
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#     joystick_flag = True
# except pygame.error:
#     joystick_flag = False
#     print("No joystick detected. Keyboard mode only.")


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

""" ROAD SETUP """
ROAD_HEIGHT = 80


""" BUTTON SETUP """
start_button_img = pygame.image.load('./sprite/start_button.png').convert_alpha()
start_button = Button(SCREEN_WIDTH//1.5, 125, start_button_img, 0.15)
anim_btn_count = 0

""" AIRCRAFT SETUP """
std_ac_anim_steps = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]

spritesheet_wheels_up = AircraftSpritesheet('./sprite/spreadsheet_aircraft_wheels_up.png', std_ac_anim_steps, 3) 
ac_wheels_up_anims = spritesheet_wheels_up.anim_list

spritesheet_wheels_down = AircraftSpritesheet('./sprite/spreadsheet_aircraft_wheels_down.png', std_ac_anim_steps, 3) 
ac_wheels_down_anims = spritesheet_wheels_down.anim_list

spritesheet_wheels_down_flap_down = AircraftSpritesheet('./sprite/spreadsheet_aircraft_wheels_down_flap.png', std_ac_anim_steps, 3) 
ac_wheels_down_flap_down_anims = spritesheet_wheels_down_flap_down.anim_list

spritesheet_wheels_up_flap_down = AircraftSpritesheet('./sprite/spreadsheet_aircraft_wheels_up_flap.png', std_ac_anim_steps, 3)
ac_wheels_up_flap_down_anims = spritesheet_wheels_up_flap_down.anim_list

spritesheet_smoke_engine_wheels_up = AircraftSpritesheet('./sprite/aircraft_smoke_wheels_up.png', [[6]], 3)
ac_smoke_engine_wheels_up_anims = spritesheet_smoke_engine_wheels_up.anim_list

spritesheet_smoke_engine_wheels_down = AircraftSpritesheet('./sprite/aircraft_smoke_wheels_down.png', [[6]], 3) 
ac_smoke_engine_wheels_down_anims = spritesheet_smoke_engine_wheels_down.anim_list

current_ac_anim_list = []

# Current animation
current_ac_anim_list = ac_wheels_up_anims

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


""" LISTEN FOR CHANGES IN THROTTLE """
throttle_time = 1000 # time window during which you can change throttle
THROTTLE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(THROTTLE_EVENT, throttle_time)

""" INSTRUCTIONS LEGEND SETUP """
legend_img = pygame.image.load('./sprite/instructions.png').convert_alpha()
gameover_img = pygame.image.load('./sprite/game_over_text.png').convert_alpha()

start_text = font.render("Press START to play:", True, (255, 255, 255))

last_update_text = pygame.time.get_ticks()

L_pressed = False
F_pressed = False

""" Flags for different game moments """

waiting_flag = True # while waiting for the START button to be pressed

show_text = True

gameover_anim_flag = True # while

ac_landed_flag = False # while aircraft is in air

freeze = False # game over screen
 
running = True # overall flag for pygame 

change_throttle = False # Did the player start to change throttle?

start_change_throttle = False # Is the player changing the throttle?

start_change_nozzle = False # Is the player changing the nozzle exit area?


""" Initial aircraft position """

ac_pos_x = SCREEN_WIDTH//9
ac_pos_y = SCREEN_HEIGHT//3 #+ 270

steady_point0 = (0, 0) # fictitious point

comp_map_width = SCREEN_WIDTH//2.5
comp_map_height = SCREEN_HEIGHT//1.7

comp_map_posx = SCREEN_WIDTH - comp_map_width - 50
comp_map_posy = SCREEN_HEIGHT - comp_map_height - 50

compressor_map, margin, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, stall, comp_map_width, comp_map_height, change_throttle, steady_point0, bg_path = r"img/bg_compressor_map.png")

while running:

    screen.fill(BG)

    for i in range(tiles):
        screen.blit(bg, (i * bg_width - scroll, 0))
        bg_rect.x = i * bg_width - scroll

    # scroll background speed
    if not ac_landed_flag:
        scroll += (throttle_dof - 50)  # throttle_dof varia tra 84 e 100
        scroll %= bg_width  # evita scatti

    else:
        if gameover_anim_flag:
            scroll += len(current_ac_anim_list) - 1 - frame
            scroll %= bg_width
            start_text = gameover_img
        elif freeze:
            show_text = True

    # Should the animation be updated if enough time has elapsed?
    current_time = pygame.time.get_ticks()
    if current_time - last_update_flame >= animation_flame:
        last_update_flame = pygame.time.get_ticks()
        if not ac_landed_flag: # if waiting for start and during landing in
            frame += 1
            if frame >= len(current_ac_anim_list[nozzle_idx]):
                frame = 0
        elif gameover_anim_flag: # if during landing on the road
            frame += 1
            if frame >= len(current_ac_anim_list):
                gameover_anim_flag = False
                freeze = True
                frame = 3
        elif freeze and not gameover_anim_flag:
            frame += 1 
            if frame >= len(current_ac_anim_list):
                frame = len(current_ac_anim_list) - 2
        
        if anim_btn_count // 2 == 0:
            anim_btn_count += 1
        else:
            anim_btn_count -= 1

    # Show the aircraft (either if it's updated or not)
    if not ac_landed_flag:
        screen.blit(current_ac_anim_list[nozzle_idx][throttle_idx][frame], (ac_pos_x, ac_pos_y))
        screen.blit(legend_img, (0, 0))
        screen.blit(compressor_map, (comp_map_posx, comp_map_posy))
        if start_change_nozzle or start_change_throttle:
            compressor_map, margin, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, stall, comp_map_width, comp_map_height, change_throttle, steady_point0, bg_path = r"img/bg_compressor_map.png")
            start_change_nozzle = False

    elif gameover_anim_flag:
        screen.blit(current_ac_anim_list[frame], (ac_pos_x, ac_pos_y))
    elif freeze:
        screen.blit(current_ac_anim_list[frame], (ac_pos_x, ac_pos_y))
    
    if start_change_throttle:
        pygame.time.set_timer(THROTTLE_EVENT, throttle_time)
        change_throttle = True
        start_change_throttle = False
    
    if waiting_flag:
        if start_button.draw(screen, anim_btn_count): # the draw method returns True when the button is pressed
            pygame.display.flip()
            waiting_flag = False
            show_text = False

            if F_pressed and L_pressed:
                current_ac_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
            else:
                if F_pressed and not L_pressed:
                    current_ac_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                elif L_pressed and not F_pressed:
                    current_ac_anim_list = aircraft_anim_list_wheels_down_scaled
                else:
                    current_ac_anim_list = aircraft_anim_list_wheels_up_scaled
    else:
        # move the aircraft
        if ac_pos_x <= SCREEN_WIDTH//1.75 and not ac_landed_flag:
            ac_pos_x += 2 

        if ac_pos_y >= (SCREEN_HEIGHT - ROAD_HEIGHT - 110):  # needs some tuning since ac_pos_y affects the position of the top left corner of the 64x64 sprite, which also has some blanck beneath the aircraft  
            ac_landed_flag = True
        elif not ac_landed_flag:
            ac_pos_y += 10
        
        # check for landing
        if ac_landed_flag and F_pressed and L_pressed:
            victory = True
        # if landed without flaps or landing gear start running animation
        elif ac_landed_flag and (not F_pressed or not L_pressed) and not freeze:
            # current_ac_anim_list = aircraft_anim_list_detach_engine[0][0]
            gameover_anim_flag = True

            if L_pressed:
                current_ac_anim_list = aircraft_anim_list_smoke_wheels_down[0][0]
            else: 
                current_ac_anim_list = aircraft_anim_list_smoke_wheels_up[0][0]

        elif freeze:
            pass
        if not F_pressed and not L_pressed:
            if waiting_flag:
                current_ac_anim_list = aircraft_anim_list_wheels_up
            elif not ac_landed_flag:
                current_ac_anim_list = aircraft_anim_list_wheels_up_scaled
            
            
    if show_text:
        if waiting_flag:
            screen.blit(start_text, (250, 140)) 
        if freeze:
            screen.blit(start_text, (SCREEN_WIDTH * 5/6, 75)) 


            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Custom event for blinking text
        elif event.type == BLINK_EVENT and waiting_flag:
            show_text = not show_text 

        elif event.type == THROTTLE_EVENT:
            if change_throttle:
                compressor_map, margin, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, stall, comp_map_width, comp_map_height, not change_throttle, steady_point0, bg_path = r"img/bg_compressor_map.png")
            change_throttle = False 
            
            
        # Listen to the keyboard
        elif event.type == pygame.KEYDOWN:

            # if not gameover_anim_flag and not freeze: # these keys must be listened only when the game is on 

                if (event.key == pygame.K_DOWN):
                    throttle_idx = max(0, throttle_idx - 1)
                    throttle_dof = max(84, throttle_dof - 0.5)

                    start_change_throttle = True
        
                    # if changing_throttle = True:
                    #     change_throttle = False
   
                    frame = 0

                if (event.key == pygame.K_UP):
                    throttle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, throttle_idx + 1)
                    throttle_dof = min(100, throttle_dof + 0.5)

                    start_change_throttle = True

                    frame = 0

                if (event.key == pygame.K_LEFT):
                    nozzle_idx = max(0, nozzle_idx - 1)
                    nozzle_dof = max(0.9, nozzle_dof - 0.05)

                    start_change_nozzle = True

                    frame = 0

                if (event.key == pygame.K_RIGHT):
                    nozzle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, nozzle_idx + 1)
                    nozzle_dof = min(1.3, nozzle_dof + 0.05)

                    start_change_nozzle = True

                    frame = 0

                if (event.key == pygame.K_l):
                    L_pressed = not L_pressed

                    if waiting_flag:
                        if F_pressed:
                            if L_pressed:
                                current_ac_anim_list = aircraft_anim_list_wheels_down_flap_down
                            else:
                                current_ac_anim_list = aircraft_anim_list_wheels_up_flap_down
                        else:
                            current_ac_anim_list = aircraft_anim_list_wheels_down
                
                    else:
                        if F_pressed:
                            if L_pressed:
                                current_ac_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                            else:
                                current_ac_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                        else:
                            current_ac_anim_list = aircraft_anim_list_wheels_down_scaled

                if (event.key == pygame.K_f):
                    F_pressed = not F_pressed

                    if waiting_flag:
                        if L_pressed:
                            if F_pressed:
                                current_ac_anim_list = aircraft_anim_list_wheels_down_flap_down
                            else:
                                current_ac_anim_list = aircraft_anim_list_wheels_down
                        else:
                            current_ac_anim_list = aircraft_anim_list_wheels_up_flap_down
                    
                    else:
                        if L_pressed:
                            if F_pressed:
                                current_ac_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                            else:
                                current_ac_anim_list = aircraft_anim_list_wheels_down_scaled
                        else:
                            current_ac_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                
                if (event.key == pygame.K_r) and freeze:
                    waiting_flag = False
                    freeze = False
                    ac_landed_flag = False
                    show_text = False
                    L_pressed = False
                    F_pressed = False
                    gameover_anim_flag = False
                    current_ac_anim_list = aircraft_anim_list_wheels_up_scaled
                    frame = 0
                    ac_pos_x = SCREEN_WIDTH//9
                    ac_pos_y = SCREEN_HEIGHT//3 #+ 270

    pygame.display.update()



pygame.quit()