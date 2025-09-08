import pygame
from src.functions import plot_compressor_map
from src.Spritesheet import Spritesheet
from src.Button import Button
import math

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

""" ROAD SETUP """
ROAD_HEIGHT = 80


""" INSTRUCTIONS LEGEND SETUP """
legend_img = pygame.image.load('./sprite/instructions.png').convert_alpha()
gameover_img = pygame.image.load('./sprite/game_over_text.png').convert_alpha()

""" BUTTON SETUP """
start_button_img = pygame.image.load('./sprite/start_button.png').convert_alpha()
start_button = Button(SCREEN_WIDTH//1.5, 125, start_button_img, 0.15)
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

spritesheet_detach_engine_png = pygame.image.load('./sprite/aircraft_gameover_ugly.png').convert_alpha() 
spritesheet_detach_engine = Spritesheet(spritesheet_detach_engine_png) 

spritesheet_smoke_engine_wheels_up_png = pygame.image.load('./sprite/aircraft_smoke_wheels_up.png').convert_alpha() 
spritesheet_smoke_engine_wheels_up = Spritesheet(spritesheet_smoke_engine_wheels_up_png) 

spritesheet_smoke_engine_wheels_down_png = pygame.image.load('./sprite/aircraft_smoke_wheels_down.png').convert_alpha() 
spritesheet_smoke_engine_wheels_down = Spritesheet(spritesheet_smoke_engine_wheels_down_png) 

""" AIRCRAFT ANIMATIONS SETUP """

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

aircraft_anim_list_detach_engine = []
aircraft_anim_steps_detach_engine = [[6]]
aircraft_anim_list_detach_engine = spritesheet_detach_engine.setup(aircraft_anim_list_detach_engine, aircraft_anim_steps_detach_engine, 3)

aircraft_anim_list_smoke_wheels_down = []
aircraft_anim_steps_smoke_wheels_down = [[6]]
aircraft_anim_list_smoke_wheels_down = spritesheet_smoke_engine_wheels_down.setup(aircraft_anim_list_smoke_wheels_down, aircraft_anim_steps_smoke_wheels_down, 3)

aircraft_anim_list_smoke_wheels_up = []
aircraft_anim_steps_smoke_wheels_up = [[6]]
aircraft_anim_list_smoke_wheels_up = spritesheet_smoke_engine_wheels_up.setup(aircraft_anim_list_smoke_wheels_up, aircraft_anim_steps_smoke_wheels_up, 3)


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


""" LISTEN FOR CHANGES IN THROTTLE """
throttle_time = 1000 # time window during which you can change throttle
THROTTLE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(THROTTLE_EVENT, throttle_time)


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
    clock.tick(120)
    if joystick_flag:
        x_js = joystick.get_axis(0)
        y_js = joystick.get_axis(1)

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
            scroll += len(aircraft_anim_list) - 1 - frame
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
            if frame >= len(aircraft_anim_list[nozzle_idx]):
                frame = 0
        elif gameover_anim_flag: # if during landing on the road
            frame += 1
            if frame >= len(aircraft_anim_list):
                gameover_anim_flag = False
                freeze = True
                frame = 3
        elif freeze and not gameover_anim_flag:
            frame += 1 
            if frame >= len(aircraft_anim_list):
                frame = len(aircraft_anim_list) - 2
        
        if anim_btn_count // 2 == 0:
            anim_btn_count += 1
        else:
            anim_btn_count -= 1

    # Show the aircraft (either if it's updated or not)
    if not ac_landed_flag:
        screen.blit(aircraft_anim_list[nozzle_idx][throttle_idx][frame], (ac_pos_x, ac_pos_y))
        screen.blit(legend_img, (0, 0))
        screen.blit(compressor_map, (comp_map_posx, comp_map_posy))
        if start_change_nozzle or start_change_throttle:
            compressor_map, margin, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, stall, comp_map_width, comp_map_height, change_throttle, steady_point0, bg_path = r"img/bg_compressor_map.png")
            start_change_nozzle = False

    elif gameover_anim_flag:
        screen.blit(aircraft_anim_list[frame], (ac_pos_x, ac_pos_y))
    elif freeze:
        screen.blit(aircraft_anim_list[frame], (ac_pos_x, ac_pos_y))
    
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
                aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
            else:
                if F_pressed and not L_pressed:
                    aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                elif L_pressed and not F_pressed:
                    aircraft_anim_list = aircraft_anim_list_wheels_down_scaled
                else:
                    aircraft_anim_list = aircraft_anim_list_wheels_up_scaled
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
            # aircraft_anim_list = aircraft_anim_list_detach_engine[0][0]
            gameover_anim_flag = True

            if L_pressed:
                aircraft_anim_list = aircraft_anim_list_smoke_wheels_down[0][0]
            else: 
                aircraft_anim_list = aircraft_anim_list_smoke_wheels_up[0][0]

        elif freeze:
            pass
        if not F_pressed and not L_pressed:
            if waiting_flag:
                aircraft_anim_list = aircraft_anim_list_wheels_up
            elif not ac_landed_flag:
                aircraft_anim_list = aircraft_anim_list_wheels_up_scaled
            
            
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
                    throttle_idx = min(len(aircraft_anim_list[nozzle_idx]) - 1, throttle_idx + 1)
                    throttle_dof = min(100, throttle_dof + 0.5)

                    start_change_throttle = True

                    frame = 0

                if (event.key == pygame.K_LEFT):
                    nozzle_idx = max(0, nozzle_idx - 1)
                    nozzle_dof = max(0.9, nozzle_dof - 0.05)

                    start_change_nozzle = True

                    frame = 0

                if (event.key == pygame.K_RIGHT):
                    nozzle_idx = min(len(aircraft_anim_list[nozzle_idx]) - 1, nozzle_idx + 1)
                    nozzle_dof = min(1.3, nozzle_dof + 0.05)

                    start_change_nozzle = True

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
                        if F_pressed:
                            if L_pressed:
                                aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                            else:
                                aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_down_scaled

                if (event.key == pygame.K_f):
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
                            if F_pressed:
                                aircraft_anim_list = aircraft_anim_list_wheels_down_flap_down_scaled
                            else:
                                aircraft_anim_list = aircraft_anim_list_wheels_down_scaled
                        else:
                            aircraft_anim_list = aircraft_anim_list_wheels_up_flap_down_scaled
                
                if (event.key == pygame.K_r) and freeze:
                    waiting_flag = False
                    freeze = False
                    ac_landed_flag = False
                    show_text = False
                    L_pressed = False
                    F_pressed = False
                    gameover_anim_flag = False
                    aircraft_anim_list = aircraft_anim_list_wheels_up_scaled
                    frame = 0
                    ac_pos_x = SCREEN_WIDTH//9
                    ac_pos_y = SCREEN_HEIGHT//3 #+ 270


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