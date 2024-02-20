""" Notes

This file is the implementation layer, and is the middle layer between command layer and modbus layer
This file contains code to initialize the serial port required to communicate with modbus devices,
and it also calls the corresponding modbus functions depending on the command action.

Function for Serial port
1. open_serial_port(port)

Functions to turn the (4) motors
2. turn_aligner_motor(modbus_port, side, direction)
side - ('left', 'right'), direction - (1: open, -1: close, 0: stop)

3. turn_platform_motor(modbus_port, side, direction)
side - ('left', 'right'), direction - (1:up, -1: down, 0: stop)



Function to check state of any of the (8) switches
4. check_limit_sensor(modbus_port, side, sensor_name) - (returns 1: pressed, 0: not pressed)

sensor_name options are as follows (convention is component_direction_sensor) and every implementation layer function needs the side to be mentioned:
(platform_up_sensor, platform_down_sensor, aligner_open_senspor, aligner_close_sensor)


"""


import serial
import hive_modbus_layer as modbus


PLATFORM_UP = 1
PLATFORM_DOWN = -1

ALIGNERS_OPEN = 1
ALIGNERS_CLOSE = -1

STOP = 0

SWITCH_PRESSED = modbus.SWITCH_PRESSED
SWITCH_NOT_PRESSED = modbus.SWITCH_NOT_PRESSED

clockwise_rotation = [modbus.RELAY_ON, modbus.RELAY_OFF]
anticlockwise_rotation = [modbus.RELAY_OFF, modbus.RELAY_ON]
stop_rotation = [modbus.RELAY_OFF, modbus.RELAY_OFF]


def open_serial_port(serial_port):
    if (serial_port != 0) and serial_port.is_open:
        pass
    else:
        serial_port = serial.Serial('dev/ttyUSB0', 9600) #to be automated

    return serial_port


def turn_aligner_motor(modbus_port, side, direction):
    if side == 'left':
        motor_relays = [1,2]
    if side == 'right':
        motor_relays = [3,4]

    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])

def turn_platform_motor(modbus_port, side, direction):
    if side == 'left':
        motor_relays = [5,6]
    if side == 'right':
        motor_relays = [7,8]

    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])


def check_limit_sensor(modbus_port, side, sensor_name):
    if side == 'left':
        sensor_channel_dict = {'platform_down_sensor': 1, 'platform_up_sensor':2, 'aligner_close_sensor':3, 'aligner_open_sensor':4}
    if side == 'right':
        sensor_channel_dict = {'platform_down_sensor': 5, 'platform_up_sensor':6, 'aligner_close_sensor':7, 'aligner_open_sensor':8} 

    return modbus.read_input_status(modbus_port,modbus.WAVESHARE_8CH, sensor_channel_dict[sensor_name]-1)
     
     

