""" Notes

This file is the implementation layer, and is the middle layer between command layer and modbus layer
This file contains code to initialize the serial port required to communicate with modbus devices,
and it also calls the corresponding modbus functions depending on the command action.


Function for Serial port
1. open_serial_port(port)
which also requires helper functions for the purpose of automating and creating a plug and play method
1.a. allow_usb_access(password) 
1.b. find_usb_port(vendor_id, product_id)

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
import hive_waveshare_constants as constants
from time import sleep

sudo_password = 'Jaima11!' #enter system's sudo password

#directions - input to functions from cmd layer
PLATFORM_UP = 1
PLATFORM_DOWN = -1

ALIGNER_OPEN = 1
ALIGNER_CLOSE = -1

STOP = 0

SWITCH_PRESSED = modbus.SWITCH_PRESSED
SWITCH_NOT_PRESSED = modbus.SWITCH_NOT_PRESSED

# if gnd/ch1 is on and live/ch2 is off, anti clockwise
#if gnd/ch1 is off and gnd/ch2 is on, clockwise
#both high, both low = stop

clockwise_rotation = [modbus.RELAY_OFF, modbus.RELAY_ON]
anticlockwise_rotation = [modbus.RELAY_ON, modbus.RELAY_OFF]
stop_rotation = [modbus.RELAY_OFF, modbus.RELAY_OFF]


#tested, all clear
def allow_usb_access():
    import subprocess
    command = f"echo {sudo_password}| sudo -S chmod a+rw /dev/ttyUSB*"

    try:
        subprocess.run(command, shell=True, check=True)
    except:
        return None


#tested, all clear
def find_usb_port(vendor_id, product_id):
    import pyudev
    context = pyudev.Context()
    for device in context.list_devices(subsystem='tty', ID_VENDOR_ID=vendor_id, ID_MODEL_ID=product_id):
        try:
            # Get the device node path
            device_node = device.device_node

            # Check if the device node path starts with /dev/ttyUSB
            if device_node.startswith('/dev/ttyUSB'):
                return device_node
        except Exception as e:
            print(f"Error: {e}")
    return 'Device not plugged in'


#tested, all clear and  works with plug and play functionality.
def open_serial_port(serial_port):
    if (serial_port != 0) and serial_port.is_open:
        pass
    else:
        # details of our usb to rs485 chip: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
        allow_usb_access() #whatever the sudo password is
        vendor_id = "0403"
        product_id = "6001"

        usb_port = find_usb_port(vendor_id, product_id)
        
        if usb_port != 'Device not plugged in':    
            serial_port = serial.Serial(usb_port, 9600)

    return serial_port


#tested, NEED TO REMAP ROTATION_DICT according to reality - rn it's dummy
#otherwise clear, works for both side A and side B aligner motors
def turn_aligner_motor(modbus_port, side, direction):
    if side == 'A':
        motor_relays = [constants.A_ALIGNER_MOTOR_GND, constants.A_ALIGNER_MOTOR_LIVE]
    if side == 'B':
        motor_relays = [constants.B_ALIGNER_MOTOR_GND, constants.B_ALIGNER_MOTOR_LIVE]

    rotation_dict = {ALIGNER_OPEN: clockwise_rotation, ALIGNER_CLOSE: anticlockwise_rotation, STOP: stop_rotation}

    i = 0
    modbus.write_relay(modbus_port,modbus.WAVESHARE_16CH,motor_relays[i],rotation_dict[direction][i])
    sleep(0.03)
    i = 1
    modbus.write_relay(modbus_port,modbus.WAVESHARE_16CH,motor_relays[i],rotation_dict[direction][i])


#tested, NEED TO REMAP ROTATION_DICT according to reality - rn it's dummy
#otherwise clear, works for both side A and side B platform motors
def turn_platform_motor(modbus_port, side, direction):
    if side == 'A':
        motor_relays = [constants.A_PLATFORM_MOTOR_GND, constants.A_PLATFORM_MOTOR_LIVE]
    if side == 'B':
        motor_relays = [constants.B_PLATFORM_MOTOR_GND, constants.B_PLATFORM_MOTOR_LIVE]
    
    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}

    i = 0
    modbus.write_relay(modbus_port,modbus.WAVESHARE_16CH,motor_relays[i],rotation_dict[direction][i])
    sleep(0.03)
    i = 1
    modbus.write_relay(modbus_port,modbus.WAVESHARE_16CH,motor_relays[i],rotation_dict[direction][i])


#tested, bug from modbus_layer fixed here by making it sleep and calling read_input_status twice so that the second
#time is the right output. Otherwise, all clear,all 8 sensors checked.
def check_limit_sensor(modbus_port, side, sensor_name):
    if side == 'A':
        sensor_channel_dict = {'platform_down_sensor': constants.A_PLATFORM_DOWN_SENSOR, 'platform_up_sensor': constants.A_PLATFORM_UP_SENSOR,
                                'aligner_close_sensor':constants.A_ALIGNER_CLOSE_SENSOR, 'aligner_open_sensor':constants.A_ALIGNER_OPEN_SENSOR}
    if side == 'B':
        sensor_channel_dict = {'platform_down_sensor': constants.B_PLATFORM_DOWN_SENSOR, 'platform_up_sensor':constants.B_PLATFORM_UP_SENSOR,
                                'aligner_close_sensor':constants.B_ALIGNER_CLOSE_SENSOR, 'aligner_open_sensor':constants.B_ALIGNER_OPEN_SENSOR} 

    input_status = modbus.read_input_status(modbus_port,modbus.WAVESHARE_8CH_1, sensor_channel_dict[sensor_name])
    sleep(0.03)
    input_status = modbus.read_input_status(modbus_port,modbus.WAVESHARE_8CH_1, sensor_channel_dict[sensor_name])

    return input_status
