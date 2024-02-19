import hive_modbus_layer as modbus

PLATFORM_UP = 1
PLATFORM_DOWN = -1

ALIGNERS_OPEN = 1
ALIGNERS_CLOSE = -1

STOP = 0

clockwise_rotation = [modbus.RELAY_ON, modbus.RELAY_OFF]
anticlockwise_rotation = [modbus.RELAY_OFF, modbus.RELAY_ON]
stop_rotation = [modbus.RELAY_OFF, modbus.RELAY_OFF]


def turn_left_aligner_motor(direction):
    motor_relays = [1,2]
    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.waveshare_32ch,motor_relays[i],rotation_dict[direction][i])

def turn_left_platform_motor(direction):
    motor_relays = [5,6]
    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.waveshare_32ch,motor_relays[i],rotation_dict[direction][i])

def turn_right_aligner_motor(direction):
    motor_relays = [3,4]
    rotation_dict = {ALIGNERS_OPEN: clockwise_rotation, ALIGNERS_CLOSE: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.waveshare_32ch,motor_relays[i],rotation_dict[direction][i])

    
def turn_right_platform_motor(direction):
    motor_relays = [7,8]
    rotation_dict = {PLATFORM_UP: clockwise_rotation, PLATFORM_DOWN: anticlockwise_rotation, STOP: stop_rotation}
    for i in range(2):
        modbus.write_relay(modbus_port,modbus.waveshare_32ch,motor_relays[i],rotation_dict[direction][i])
