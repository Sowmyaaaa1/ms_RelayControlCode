"""
This file is the implementation layer, and is the middle layer between command layer and modbus layer
This file contains code to initialize the serial port required to communicate with modbus devices,
and it also calls the corresponding modbus functions depending on the command action.

Function for Serial port
1. open_serial_port()

Functions to turn the (4) motors
2. turn_left_aligner_motor(modbus_port, direction), direction - (1: open, -1: close, 0: stop)
3. turn_left_platform_motor(modbus_port, direction), direction - (1:up, -1: down, 0: stop)
4. turn_right_aligner_motor(modbus_port, direction), direction - (1: open, -1: close, 0: stop)
5. turn_right_platform_motor(modbus_port, direction), direction - (1:up, -1: down, 0: stop)

Function to check state of any of the (8) switches
6. check_limit_sensor(modbus_port, sensor_name) - (1: pressed, 0: not pressed)
   sensor_name options: (left_platform_up, left_platform_down, left_aligner_open, left_aligner_close, right_platform_up, right_platform_down, 
   right_aligner_close, right_aligner_open)
"""


import serial
import hive_modbus_layer as modbus


PLATFORM_UP = 1
PLATFORM_DOWN = -1

ALIGNERS_OPEN = 1
ALIGNERS_CLOSE = -1

STOP = 0

clockwise_rotation = [modbus.RELAY_ON, modbus.RELAY_OFF]
anticlockwise_rotation = [modbus.RELAY_OFF, modbus.RELAY_ON]
stop_rotation = [modbus.RELAY_OFF, modbus.RELAY_OFF]


def open_serial_port():
    #to be written
    pass


def turn_left_aligner_motor(modbus_port, direction):
    motor_relays = [1,2]
    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])

def turn_left_platform_motor(modbus_port, direction):
    motor_relays = [5,6]
    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])

def turn_right_aligner_motor(modbus_port, direction):
    motor_relays = [3,4]
    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])

    
def turn_right_platform_motor(modbus_port, direction):
    motor_relays = [7,8]
    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])


def check_limit_sensor(modbus_port, sensor_name):
    sensor_channel_dict = {'left_platform_down': 1, 'left_platform_up':2, 'left_aligner_close':3, 
                           'left_aligner_open':4,'right_platform_down': 5, 'right_platform_up':6, 'right_aligner_close':7, 'right_aligner_open':8} 
    return modbus.read_input_status(modbus_port,modbus.WAVESHARE_8CH, sensor_channel_dict[sensor_name]-1)
     

