from src.objects.Spritesheet import AircraftSpritesheet
from src.functions.interface_functions import isHomeScreen_event_listener, isFlying_keyboard_listener, unpack_current_state, pack_current_state
from src.objects.Button import Button
from src.functions.game_functions import plot_compressor_map


import pygame
import math

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750
BG = (0, 181, 226) # Blue Sky RGB color

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

""" BACKGROUND SETUP """

bg = pygame.image.load(f"./sprite/background.png").convert()
bg_width = bg.get_width()
bg_rect = bg.get_rect()

# Define game variables
scroll = 0
tiles = math.ceil(SCREEN_WIDTH  / bg_width) + 1


# The road is not a stand-alone object, so we cannot collide with it. It's height is:
ROAD_HEIGHT = 80

""" BUTTON SETUP """

start_button_img = pygame.image.load('./sprite/start_button.png').convert_alpha()
start_button = Button(SCREEN_WIDTH//1.5, 125, start_button_img, 0.15)
anim_btn_count = 0


""" AIRCRAFT ANIMATIONS SETUP """

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

aircraft_anims = {
        "ac_wheels_up_flap_up_anims" : ac_wheels_up_anims,
        "ac_wheels_down_flap_up_anims" : ac_wheels_down_anims,
        "ac_wheels_down_flap_down_anims" : ac_wheels_down_flap_down_anims,
        "ac_wheels_up_flap_down_anims" : ac_wheels_up_flap_down_anims,
        "ac_smoke_engine_wheels_up_anims" : ac_smoke_engine_wheels_up_anims,
        "ac_smoke_engine_wheels_down_anims" : ac_smoke_engine_wheels_down_anims     
}

last_update_flame = pygame.time.get_ticks()
animation_flame = 300


""" FLAGS SETUP """

isGameOn = True

isHomeScreen = True

isFlying = False

isLanded = False

""" AIRCRAFT INITIAL STATE """

ac_pos_x, ac_pos_y = 100, 100 # [Pixel] From top-left corner 

initial_state = {
        "throttle_idx" : 0,
        "throttle_dof" : 92,
        "nozzle_idx" : 0,
        "nozzle_dof" : 1.1,
        "frame" : 0,
        "current_ac_anim_list" : spritesheet_wheels_up.anim_list,
        "F_pressed" : False,
        "L_pressed" : False,
        "start_change_throttle" : False,
        "start_change_nozzle" : False,
        "isStalled": False,
        "ac_pos": (ac_pos_x, ac_pos_y)
}

current_state = initial_state.copy()


throttle_idx, throttle_dof, nozzle_idx, \
nozzle_dof, frame, current_ac_anim_list, \
F_pressed, L_pressed, start_change_throttle, \
start_change_nozzle, isStalled, ac_pos = unpack_current_state(current_state)


""" COMPRESSOR MAP SETUP """
steady_point0 = (15, 5) # fictitious point

comp_map_width = SCREEN_WIDTH//3
comp_map_height = SCREEN_HEIGHT//2

comp_map_posx = SCREEN_WIDTH - comp_map_width - 50
comp_map_posy = SCREEN_HEIGHT - comp_map_height - 150

isThrottleChanging = False

compressor_map, margin, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, False, comp_map_width, comp_map_height, isThrottleChanging, steady_point0, bg_path = r"img/bg_compressor_map.png")

# Start a timer of the duration of throttle_time to stop listening for throttle changes

throttle_time = 1000 # time window during which the player can change the throttle
THROTTLE_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(THROTTLE_EVENT, throttle_time)


while isGameOn:

    screen.fill(BG)

    if isHomeScreen:
        
        """ ANIMATIONS UPDATE """

        # Setting up scrolling background (constant scroll speed)
        scroll += 100 
        scroll %= bg_width  
        
        for i in range(tiles):
            screen.blit(bg, (i * bg_width - scroll, 0))
            bg_rect.x = i * bg_width - scroll


        # Flame animation
        current_time = pygame.time.get_ticks()
        if current_time - last_update_flame >= animation_flame:
            last_update_flame = pygame.time.get_ticks()
            frame += 1
            if frame >= std_ac_anim_steps[nozzle_idx][throttle_idx]:
                frame = 0

        # Compressor map animation
        compressor_map, _, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, False, comp_map_width, comp_map_height, isThrottleChanging, steady_point0, bg_path = r"img/bg_compressor_map.png")
    

        """ BLIT  UPDATED ANIMATIONS """

        screen.blit(current_ac_anim_list[nozzle_idx][throttle_idx][frame], (ac_pos_x, ac_pos_y))

        screen.blit(compressor_map, (comp_map_posx, comp_map_posy))
        

        """ EVENT LISTENER """

        current_state = pack_current_state( throttle_idx, throttle_dof, nozzle_idx, 
                                        nozzle_dof, frame, current_ac_anim_list, 
                                        F_pressed, L_pressed, start_change_throttle, 
                                        start_change_nozzle, current_state)

        isGameOn, current_state, frame, isThrottleChanging = isHomeScreen_event_listener(isGameOn, current_state, aircraft_anims, (THROTTLE_EVENT, isThrottleChanging))

        throttle_idx, throttle_dof, nozzle_idx, \
        nozzle_dof, frame, current_ac_anim_list, \
        F_pressed, L_pressed, start_change_throttle, \
        start_change_nozzle, _, _ = unpack_current_state(current_state)

        """ Custom events listener """
        
        if start_change_throttle:
            pygame.time.set_timer(THROTTLE_EVENT, throttle_time)
            start_change_throttle = False
            isThrottleChanging = True

        """ SWITCH TO NEXT PHASE """

        if start_button.draw(screen, anim_btn_count): 
            print("game started")
            pygame.display.flip()
            isHomeScreen = False
            isFlying = True
            
            # Initialize current_state before starting the game:
            current_state = initial_state.copy()

    elif isFlying:
        
        """ ANIMATIONS UPDATE """

        # Setting up scrolling background 

        # TODO: Scroll speed should be a function of flap y/n and throttle_dof
        scroll += 100 
        scroll %= bg_width  
        
        for i in range(tiles):
            screen.blit(bg, (i * bg_width - scroll, 0))
            bg_rect.x = i * bg_width - scroll


        # Flame animation (is the same)
        current_time = pygame.time.get_ticks()
        if current_time - last_update_flame >= animation_flame:
            last_update_flame = pygame.time.get_ticks()
            frame += 1
            if isStalled:
                if frame >= 6:
                    frame = 4
            else:
                if frame >= std_ac_anim_steps[nozzle_idx][throttle_idx]:
                    frame = 0


        # Compressor map animation (now we check for stall)
        compressor_map, isStalled, steady_point0 = plot_compressor_map(throttle_dof, nozzle_dof, isStalled, comp_map_width, comp_map_height, isThrottleChanging, steady_point0, bg_path = r"img/bg_compressor_map.png")

        if isStalled:
            throttle_idx = 0
            nozzle_idx = 0
            if L_pressed:
                current_ac_anim_list = aircraft_anims["ac_smoke_engine_wheels_down_anims"]
            else:
                current_ac_anim_list = aircraft_anims["ac_smoke_engine_wheels_up_anims"]

        # Aircraft animation

        if ac_pos_x <= SCREEN_WIDTH//2.5:
            if F_pressed:
                if L_pressed: 
                    ac_pos_x += 1 # Flap AND LandGear (slowest)
                    ac_pos_y += 4
                else:
                    ac_pos_x += 2 # Flap NO LandGear (slow)
                    ac_pos_y += 3
            else:
                if L_pressed: 
                    ac_pos_x += 3 # LandGear NO Flap (fast)
                    ac_pos_y += 2
                else:
                    ac_pos_x += 4 # NO LandGear NO Flap (fastest)
                    ac_pos_y += 1

        
            
            

        ac_pos = (ac_pos_x, ac_pos_y)


        """ BLIT  UPDATED ANIMATIONS """
        if not isStalled:
            screen.blit(current_ac_anim_list[nozzle_idx][throttle_idx][frame], (ac_pos_x, ac_pos_y))
        else:
            print(current_ac_anim_list)
            screen.blit(current_ac_anim_list[nozzle_idx][throttle_idx][frame], (ac_pos_x, ac_pos_y))
       

        screen.blit(compressor_map, (comp_map_posx, comp_map_posy))
        

        """ EVENT LISTENER """


        # Repack every change that has been made to the ac current state into current_state
        current_state = pack_current_state(throttle_idx, throttle_dof, nozzle_idx, 
                                        nozzle_dof, frame, current_ac_anim_list, 
                                        F_pressed, L_pressed, start_change_throttle, 
                                        start_change_nozzle, current_state, isStalled, ac_pos)

        # Listen for eventual changes
        isGameOn, current_state, frame, isThrottleChanging = isFlying_keyboard_listener(isGameOn, current_state, aircraft_anims, (THROTTLE_EVENT, isThrottleChanging))

        # Repack eventual changes into current_state
        throttle_idx, throttle_dof, nozzle_idx, \
        nozzle_dof, frame, current_ac_anim_list, \
        F_pressed, L_pressed, start_change_throttle, \
        start_change_nozzle, isStalled, ac_pos = unpack_current_state(current_state)

        """ Custom events listener """
        
        if start_change_throttle:
            pygame.time.set_timer(THROTTLE_EVENT, throttle_time)
            start_change_throttle = False
            isThrottleChanging = True

        """ SWITCH TO NEXT PHASE """

        if ac_pos_y >= (SCREEN_HEIGHT - ROAD_HEIGHT - 110): # 110 because needs some tuning (no collision)
            pygame.display.flip()
            isFlying = False
            isLanded = True
    
    elif isLanded:  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    isGameOn = False
    
    pygame.display.flip()

pygame.quit()