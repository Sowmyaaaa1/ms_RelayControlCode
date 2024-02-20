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
import pyudev
import hive_modbus_layer as modbus
import hive_waveshare_constants as constants

sudo_password = 'password' #enter your password

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

def allow_usb_access():
    import subprocess
    command = f"echo {sudo_password}| sudo -S chmod a+rw /dev/ttyUSB*"

    try:
        subprocess.run(command, shell=True, check=True)
    except:
        return None


def find_usb_port(vendor_id, product_id):
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


def turn_aligner_motor(modbus_port, side, direction):
    if side == 'left':
        motor_relays = [constants.LEFT_ALIGNER_MOTOR_A, constants.LEFT_ALIGNER_MOTOR_B]
    if side == 'right':
        motor_relays = [constants.RIGHT_ALIGNER_MOTOR_A, constants.RIGHT_ALIGNER_MOTOR_B]

    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])

def turn_platform_motor(modbus_port, side, direction):
    if side == 'left':
        motor_relays = [constants.LEFT_PLATFORM_MOTOR_A, constants.LEFT_PLATFORM_MOTOR_B]
    if side == 'right':
        motor_relays = [constants.RIGHT_PLATFORM_MOTOR_A, constants.RIGHT_PLATFORM_MOTOR_B]

    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.WAVESHARE_32CH,motor_relays[i],rotation_dict[direction][i])


def check_limit_sensor(modbus_port, side, sensor_name):
    if side == 'left':
        sensor_channel_dict = {'platform_down_sensor': constants.LEFT_PLATFORM_DOWN_SENSOR, 'platform_up_sensor': constants.LEFT_PLATFORM_UP_SENSOR,
                                'aligner_close_sensor':constants.LEFT_ALIGNER_CLOSE_SENSOR, 'aligner_open_sensor':constants.LEFT_ALIGNER_OPEN_SENSOR}
    if side == 'right':
        sensor_channel_dict = {'platform_down_sensor': constants.RIGHT_PLATFORM_DOWN_SENSOR, 'platform_up_sensor':constants.RIGHT_PLATFORM_UP_SENSOR,
                                'aligner_close_sensor':constants.RIGHT_ALIGNER_CLOSE_SENSOR, 'aligner_open_sensor':constants.RIGHT_ALIGNER_OPEN_SENSOR} 

    return modbus.read_input_status(modbus_port,modbus.WAVESHARE_8CH, sensor_channel_dict[sensor_name]-1)
     
     

