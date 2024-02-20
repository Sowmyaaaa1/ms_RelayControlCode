
"""Notes
This file contains the functions that will be directly called by the port manager to operate the docking station. It makes use of the implementation layer, 
which inturn makes use of the modbus layer to implement the required commands.

The command functions are as follows

1. cmd_platform_up(side)  side = 'left' or 'right'
2. cmd_platform_down(side) side = 'left' or 'right'
3. cmd_aligners_open(side) side = 'left' or 'right'
4. cmd_aligners_close(side) side = 'left' or 'right'

The operator also needs constant status updates about the current status of the platform and aligners at any point of time, even in between command execution.
The variables that will hold the states will be in a dictionary format:

platform_status_dict = {'left': INITIAL_STATE, 'right':INITIAL_STATE}
aligner_status_dict =  {'left': INITIAL_STATE, 'right':INITIAL_STATE}

To the operator, the string will be printed with the side in question first, followed by the status of the relevant component on that side. 
Below is the mapping for status vs what is printed.

platform_status_display_map = {DOWN: 'platform is down', UP: 'platform is up', GOING_UP: 'platform going up', GOING_DOWN: 'platform going down', 
                             FUNNY: 'platform funny readings', INITIAL_STATE: 'platform is in initial state'}
aligner_status_display_map= {CLOSED : 'aligner is closed', OPENED: 'aligner is open', OPENING:'aligner is opening', CLOSING:'aligner is closing',
                             FUNNY: 'aligner funny readings',INITIAL_STATE: 'aligner is in initial state'}
 
Important checks or conditions to execute a command are as follows:
1. platform can go up and down only when aligners are closed.
2. aligners can open or close only when platform is up.

3. platform go up or down only if gate is open
4. the gate can close or open only when platform is down

sensor_name options are as follows (convention is component_direction_sensor) and every implementation layer function needs the side to be mentioned:

(platform_up_sensor, platform_down_sensor, aligner_open_senspor, aligner_close_sensor)

"""

#all neccesary imports
import hive_implementation_layer as imp
import serial
from time import sleep

#modbus port global variable : is zero if no port, else is a serial object. Any function can update
modbus_port = 0

#defining state mapping
CLOSED = 0; OPENED = 1; OPENING = 2; CLOSING = 3; 
DOWN = 0; UP = 1; GOING_UP = 2; GOING_DOWN = 3; 
FUNNY = 4 ; INITIAL_STATE = 10
#defining status variables, any function can update any state


platform_status_dict = {'left': INITIAL_STATE, 'right':INITIAL_STATE}
aligner_status_dict =  {'left': INITIAL_STATE, 'right':INITIAL_STATE}



platform_status_display_map = {DOWN: 'platform is down', UP: 'platform is up', GOING_UP: 'platform going up', GOING_DOWN: 'platform going down', 
                             FUNNY: 'platform funny readings', INITIAL_STATE: 'platform is in initial state'}
aligner_status_display_map= {CLOSED : 'aligner is closed', OPENED: 'aligner is open', OPENING:'aligner is opening', CLOSING:'aligner is closing',
                             FUNNY: 'aligner funny readings',INITIAL_STATE: 'aligner is in initial state'}


def check_platform_status(side):

    platform_down_sensor_status = imp.check_limit_sensor(modbus_port, side, 'platform_down_sensor')
    platform_up_sensor_status = imp.check_limit_sensor(modbus_port, side, 'platform_up_sensor')

    platform_sensor_list = [platform_down_sensor_status, platform_up_sensor_status]
    
    if platform_sensor_list == [imp.SWITCH_PRESSED, imp.SWITCH_PRESSED]:
        platform_status_dict[side] = FUNNY
    elif platform_sensor_list == [imp.SWITCH_PRESSED, imp.SWITCH_NOT_PRESSED]:
        platform_status_dict[side] = DOWN
    elif platform_sensor_list == [imp.SWITCH_NOT_PRESSED, imp.SWITCH_PRESSED]:
        platform_status_dict[side] = UP


def check_aligner_status(side):

    aligner_close_sensor_status = imp.check_limit_sensor(modbus_port, side,'aligner_close_sensor')
    aligner_open_sensor_status = imp.check_limit_sensor(modbus_port, side,'aligner_close_status')

    aligner_sensor_list = [aligner_close_sensor_status, aligner_open_sensor_status]

    if aligner_sensor_list == [imp.SWITCH_PRESSED, imp.SWITCH_PRESSED]:
        aligner_status_dict[side] = FUNNY
    elif aligner_sensor_list == [imp.SWITCH_PRESSED, imp.SWITCH_NOT_PRESSED]:
        aligner_status_dict[side] = CLOSED
    elif aligner_sensor_list == [imp.SWITCH_NOT_PRESSED, imp.SWITCH_PRESSED]:
        aligner_status_dict[side] = OPENED


def cmd_platform_up(side):
   '''Code flow (without gate status)
    1. check serial port
    2. update status variables
    3. check if aligners are closed, if yes proceed, if not tell operator the status and exit
    4. if funny platform, tell operator, stop motor and exit
    5. finally, unitl upper switch not pressed, turn motor to go up. I am not checking if motor is down at the start incase previous run was aborted midway.
    6. once pressed, update platform status to up and exit
    '''
   modbus_port = imp.open_serial_port(modbus_port)

   check_platform_status(side)
   check_aligner_status(side)

   if aligner_status_dict[side] != CLOSED:
      return (side, aligner_status_display_map[aligner_status_dict[side]]) #or print

   while True:
      check_platform_status(side)

      if platform_status_dict[side]== FUNNY:
         break 

      elif platform_status_dict[side] == UP:
         break
      
      else:
         imp.turn_platform_motor(modbus_port, side, direction=imp.PLATFORM_UP)
         platform_status_dict[side] = GOING_UP

   imp.turn_platform_motor(modbus_port, side, direction=imp.STOP)
   return (side, aligner_status_display_map[aligner_status_dict[side]])



def cmd_platform_down(side):
    '''code flow (without gate status)
    1. check serial port
    2. check if aligners are closed, if yes proceed, if not tell operator that aligners aren't closed and exit, set aligner state
    3. check platform sensor status and update status variable. if both pressed do funny
    4. if lower switch not pressed, turn motor to go down. loop this until switch is pressed, keep updating platform status
    5. once pressed, update platform status to down and exit
    '''
    modbus_port = imp.open_serial_port(modbus_port)

    check_platform_status(side)
    check_aligner_status(side)

    if aligner_status_dict[side] != CLOSED:
        return (side, aligner_status_display_map[aligner_status_dict[side]]) # or print

    while True:
        check_platform_status(side)

        if platform_status_dict[side]== FUNNY:
            break 

        elif platform_status_dict[side] == DOWN:
            break
        
        else:
            imp.turn_platform_motor(modbus_port, side, direction=imp.PLATFORM_DOWN)
            platform_status_dict[side] = GOING_DOWN

    imp.turn_platform_motor(modbus_port, side, direction=imp.STOP)
    return (side, aligner_status_display_map[aligner_status_dict[side]])



    
def cmd_aligners_open(side):
    '''code flow (without gate status)
    1. check serial port
    2. check if platform is up, if yes proceed, if not tell operator and update state variable and exit
    3. check aligner sensor status and update state variable
    4. check if open switch is pressed, if not turn motor to open.  do in loop until switch pressed and keep updating aligner status
    5. once pressed update aligner status to open and exit
    '''
    modbus_port = imp.open_serial_port(modbus_port)

    check_platform_status(side)
    check_aligner_status(side)

    if platform_status_dict[side] != UP:
        return (side, platform_status_display_map[platform_status_dict[side]]) # or print
    
    while True:
        check_aligner_status(side)

        if aligner_status_dict[side] == FUNNY:
            break

        elif aligner_status_dict[side] == OPENED:
            break
        
        else:
            imp.turn_aligner_motor(modbus_port, side, direction= imp.ALIGNERS_OPEN)
            aligner_status_dict[side] = OPENING

    imp.turn_aligner_motor(modbus_port, side, direction=imp.STOP)
    return (side, aligner_status_display_map[aligner_status_dict[side]]) # or print



def cmd_aligners_close(side):
    '''code flow (without gate status)
    1. check serial port
    2. check if platform is up, if yes proceed, if not tell operator and update state variable and exit
    3. check aligner sensor status and update state variable
    4. check if close switch is pressed, if not turn motor to close.  do in loop until switch pressed and keep updating aligner status
    5. once pressed update aligner status to close and exit
    '''
    modbus_port = imp.open_serial_port(modbus_port)

    check_platform_status(side)
    check_aligner_status(side)

    if platform_status_dict[side] != UP:
        return (side, platform_status_display_map[platform_status_dict[side]]) # or print
    
    while True:
        check_aligner_status(side)

        if aligner_status_dict[side] == FUNNY:
            break

        elif aligner_status_dict[side] == CLOSED:
            break
        
        else:
            imp.turn_aligner_motor(modbus_port, side, direction= imp.ALIGNERS_CLOSE)
            aligner_status_dict[side] = CLOSING

    imp.turn_aligner_motor(modbus_port, side, direction=imp.STOP)
    return (side, aligner_status_display_map[aligner_status_dict[side]]) # or print
