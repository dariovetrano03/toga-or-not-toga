import sys
import os
import pygame

from math import ceil

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
pparent_dir = os.path.dirname(parent_dir)

sys.path.append(pparent_dir)  # Add top-level folder to Python path

from src.functions.game_functions import plot_compressor_map

min_throttle_dof = 84
max_throttle_dof = 100
min_nozzle_dof = 0.9
max_nozzle_dof = 1.1

delta_throttle_dof = 0.5
delta_nozzle_dof = 0.025

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 750

def pack_current_state(
    throttle_idx, throttle_dof, nozzle_idx, 
    nozzle_dof, frame, current_ac_anim_list, 
    F_pressed, L_pressed, start_change_throttle, 
    start_change_nozzle, current_state, 
    isStalled = False, ac_pos = (0, 0), 
):
    
    current_state["throttle_idx"] = throttle_idx 
    current_state["throttle_dof"] = throttle_dof 
    current_state["nozzle_idx"] = nozzle_idx 
    current_state["nozzle_dof"] = nozzle_dof

    current_state["frame"] = frame

    current_state["current_ac_anim_list"] = current_ac_anim_list

    current_state["F_pressed"] = F_pressed
    current_state["L_pressed"] = L_pressed
    current_state["start_change_throttle"] = start_change_throttle
    current_state["start_change_nozzle"] = start_change_nozzle
    current_state["isStalled"] = isStalled
    current_state["ac_pos"] = ac_pos

    return current_state

def unpack_current_state(current_state):
    throttle_idx = current_state["throttle_idx"]
    throttle_dof = current_state["throttle_dof"]
    nozzle_idx = current_state["nozzle_idx"]
    nozzle_dof = current_state["nozzle_dof"]

    frame = current_state["frame"]

    current_ac_anim_list = current_state["current_ac_anim_list"]

    F_pressed = current_state["F_pressed"]
    L_pressed = current_state["L_pressed"]
    start_change_throttle = current_state["start_change_throttle"]
    start_change_nozzle = current_state["start_change_nozzle"]

    isStalled = current_state["isStalled"]
    ac_pos = current_state["ac_pos"]

    return throttle_idx, throttle_dof, nozzle_idx, nozzle_dof, frame, \
    current_ac_anim_list, F_pressed, L_pressed, start_change_throttle, \
    start_change_nozzle, isStalled, ac_pos


def isHomeScreen_event_listener(isGameOn, current_state, aircraft_anims, *custom_events,):

    throttle_idx, throttle_dof, nozzle_idx, \
    nozzle_dof, frame, current_ac_anim_list, \
    F_pressed, L_pressed, start_change_throttle, \
    start_change_nozzle, _, _ = unpack_current_state(current_state)

    THROTTLE_EVENT, isThrottleChanging = custom_events[0]

    for event in pygame.event.get():

        if event.type == pygame.QUIT:  
            isGameOn = False
            continue
        
        elif event.type == THROTTLE_EVENT:
            if isThrottleChanging:
                isThrottleChanging = False

        elif event.type == pygame.KEYDOWN:


            if (event.key == pygame.K_DOWN):
                throttle_idx = max(0, throttle_idx - 1)
                throttle_dof = max(min_throttle_dof, throttle_dof - delta_throttle_dof)

                start_change_throttle = True
    
                frame = 0

            if (event.key == pygame.K_UP):
                throttle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, throttle_idx + 1)
                throttle_dof = min(max_throttle_dof, throttle_dof + delta_throttle_dof)

                start_change_throttle = True

                frame = 0

            if (event.key == pygame.K_LEFT):
                nozzle_idx = max(0, nozzle_idx - 1)
                nozzle_dof = max(min_nozzle_dof, nozzle_dof - delta_nozzle_dof)

                start_change_nozzle = True

                frame = 0

            if (event.key == pygame.K_RIGHT):
                nozzle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, nozzle_idx + 1)
                nozzle_dof = min(max_nozzle_dof, nozzle_dof + delta_nozzle_dof)

                start_change_nozzle = True

                frame = 0

            if (event.key == pygame.K_l):
                L_pressed = not L_pressed

                if L_pressed:
                    if F_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_up_anims"]
                else:
                    if F_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_up_anims"]
        
                
            if (event.key == pygame.K_f):
                F_pressed = not F_pressed

                if F_pressed:
                    if L_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_down_anims"]
                else:
                    if L_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_up_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_up_anims"]
        

    current_state = pack_current_state(throttle_idx, throttle_dof, nozzle_idx, 
                                        nozzle_dof, frame, current_ac_anim_list, 
                                        F_pressed, L_pressed, start_change_throttle, 
                                        start_change_nozzle, current_state)


    return isGameOn, current_state, frame, isThrottleChanging


def isFlying_keyboard_listener(isGameOn, current_state, aircraft_anims,  *custom_events):

    throttle_idx, throttle_dof, nozzle_idx, \
    nozzle_dof, frame, current_ac_anim_list, \
    F_pressed, L_pressed, start_change_throttle, \
    start_change_nozzle, isStalled, ac_pos = unpack_current_state(current_state)

    THROTTLE_EVENT, isThrottleChanging = custom_events[0]

    for event in pygame.event.get():

        if event.type == pygame.QUIT:  
            isGameOn = False
            continue
        
        elif event.type == THROTTLE_EVENT:
            if isThrottleChanging:
                isThrottleChanging = False

        elif event.type == pygame.KEYDOWN:

            if (event.key == pygame.K_DOWN):
                throttle_idx = max(0, throttle_idx - 1)
                throttle_dof = max(min_throttle_dof, throttle_dof - delta_throttle_dof)

                start_change_throttle = True
    
                frame = 0

            if (event.key == pygame.K_UP):
                throttle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, throttle_idx + 1)
                throttle_dof = min(max_throttle_dof, throttle_dof + delta_throttle_dof)

                start_change_throttle = True

                frame = 0

            if (event.key == pygame.K_LEFT):
                nozzle_idx = max(0, nozzle_idx - 1)
                nozzle_dof = max(min_nozzle_dof, nozzle_dof - delta_nozzle_dof)

                start_change_nozzle = True

                frame = 0

            if (event.key == pygame.K_RIGHT):
                nozzle_idx = min(len(current_ac_anim_list[nozzle_idx]) - 1, nozzle_idx + 1)
                nozzle_dof = min(max_nozzle_dof, nozzle_dof + delta_nozzle_dof)

                start_change_nozzle = True

                frame = 0

            if (event.key == pygame.K_l):
                L_pressed = not L_pressed

                if L_pressed:
                    if F_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_up_anims"]
                else:
                    if F_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_up_anims"]
        
                
            if (event.key == pygame.K_f):
                F_pressed = not F_pressed

                if F_pressed:
                    if L_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_down_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_down_anims"]
                else:
                    if L_pressed:
                        current_ac_anim_list = aircraft_anims["ac_wheels_down_flap_up_anims"]
                    else:
                        current_ac_anim_list = aircraft_anims["ac_wheels_up_flap_up_anims"]
        

    current_state = pack_current_state( throttle_idx, throttle_dof, nozzle_idx, 
                                        nozzle_dof, frame, current_ac_anim_list, 
                                        F_pressed, L_pressed, start_change_throttle, 
                                        start_change_nozzle, current_state, isStalled, ac_pos)


    return isGameOn, current_state, frame, isThrottleChanging


