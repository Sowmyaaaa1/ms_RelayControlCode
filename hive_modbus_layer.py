"""Notes

This file contains the functions required to communicate with the waveshare modules.

There are 2 waveshare devices in use
1. 8 channel waveshare as INPUT device that reads limit switch position. User is able to access all 8 channels.
2. 32 channel waveshare as OUTPUT device that actuates the motors. User is able to access all 32 channels

The (4) functions are:

Tool Functions
1. add_crc16(cmd_without_crc16)

Function for Input 8ch:
2. read_input_status(serial_object,device_address, channel_number)

Function for Output 32ch:
3. turn_on_relay(serial_object, device_address, channel_number)
4. turn_off_relay(serial_object, device_address, channel_number)


"""


#imports
from time import sleep
import serial
#variables 
RELAY_ON = 1
RELAY_OFF = 0

SWITCH_PRESSED = 1
SWITCH_NOT_PRESSED = 0

#device addresses
WAVESHARE_8CH_1 = 1
WAVESHARE_16CH = 2
WAVESHARE_8CH_2 = 3


#functions

#tested, works for all possible cases
def add_crc16(cmd_without_crc16):  #https://stackoverflow.com/questions/69369408/calculating-crc16-in-python-for-modbus
    def modbusCrc(msg:str) -> int:
        crc = 0xFFFF
        for n in range(len(msg)):
            crc ^= msg[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    hex_string = ''
    for i in cmd_without_crc16[:6]:
        s = str(hex(i).split('x')[1])
        if len(s) == 1 :
            s = '0' + s
        hex_string += s
        msg = bytes.fromhex(hex_string)

    modbusCrc(msg)
    crc = modbusCrc(msg)         

    ba = crc.to_bytes(2, byteorder='little')
    cmd_without_crc16[6]= int(ba[0])
    cmd_without_crc16[7] = int(ba[1])
    return cmd_without_crc16


#tested, 1 bug everything else clear. works on all 8 channels. 
#quick fix of bus implemented in implementation layer check_input_status function
#bug: only on the second try after switch is pressed does the value actually change
def read_input_status(serial_object,device_address, channel_number):
    cmd_without_crc16 = [device_address,0x02,0x00,0x00,0x00,0x08,0x79,0xCC] #0x01 is address of first 8ch device
    cmd_to_send = add_crc16(cmd_without_crc16)
    serial_object.write(cmd_to_send)
    reply = list(serial_object.read_all())
    try:
        input_status = reply[3]
    except:
        return -1
    
    channel_status = input_status & (1 << (channel_number-1)) 
    ##pressed is 0, not pressed is 1 for limit switch
    if channel_status == 0:
        return SWITCH_PRESSED
    else:
        return SWITCH_NOT_PRESSED
    
    
#tested, fast response, all clear. works on all 16 channels.
def write_relay(serial_object, device_address, channel_number, relay_cmd):
    if relay_cmd == RELAY_ON: 
        cmd_without_crc16 = [device_address,0x05,0x00,channel_number-1,0xFF,0x00,0x00,0x00]
    elif relay_cmd == RELAY_OFF:
        cmd_without_crc16 = [device_address,0x05,0x00,channel_number-1,0x00,0x00,0x00,0x00]
    cmd_to_send = add_crc16(cmd_without_crc16)
    serial_object.write(cmd_to_send)
    reply = list(serial_object.read_all())
    return   

