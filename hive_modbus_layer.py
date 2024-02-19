"""Note

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




def add_crc16(cmd_without_crc16):
    def crc_calculator(msg:str) -> int: 
        for n in range(len(msg)):
            crc ^= msg[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    full_hex_str = ''
    list = cmd_without_crc16
    for i in range(6):
        str_of_hex =(hex(list[i]).split('x')[1])
        if len(str_of_hex) == 1:
            str_of_hex = '0'+str_of_hex
        full_hex_str = full_hex_str + str_of_hex
    msg = bytes.fromhex(full_hex_str)
    crc = crc_calculator(msg)
    list[6] = int(hex(crc)[4:], 16)
    list[7] = int(hex(crc)[2:4], 16)
    return list


def read_input_status(serial_object,device_address, channel_number):
    cmd_to_send = [device_address,0x02,0x00,0x00,0x00,0x08,0x79,0xCC] #0x01 is address of first 8ch device
    serial_object.write(cmd_to_send)
    print(cmd_to_send)
    reply = list(serial_object.read_all())
    print(cmd_to_send)
    print(reply)
    input_status = reply[3]
    channel_status = input_status & (1 << (channel_number-1)) 
    ##pressed is 0, not pressed is 1 for limit switch
    if channel_status:
        return "not pressed"
    else:
        return "pressed"
    

def turn_on_relay(serial_object, device_address, channel_number):
    cmd_without_crc16 = [device_address,0x05,0x00,channel_number-1,0xFF,0x00,0x00,0x00]
    cmd_to_send = add_crc16(cmd_without_crc16)
    serial_object.write(cmd_to_send)
    reply = list(serial_object.read_all())
    print(cmd_to_send)
    print(reply)
    return   
  

def turn_off_relay(serial_object, device_address, channel_number):
    cmd_without_crc16 = [device_address,0x05,0x00,channel_number-1,0x00,0x00,0x00,0x00]
    cmd_to_send = add_crc16(cmd_without_crc16)
    serial_object.write(cmd_to_send)
    reply = list(serial_object.read_all())
    print(cmd_to_send)
    print(reply)
    return   
