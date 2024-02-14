import minimalmodbus

def set_device_address(port_name):
    desired_address = device_address
    broadcast_address = 0
    command_register = int(0x4000)
    temp_instrument = minimalmodbus.Instrument(port_name, broadcast_address)
    temp_instrument.write_register(command_register, desired_address, functioncode=SET_ADDRESS_AND_BAUDRATE)
    #raw_data_from_slave = temp_instrument._communicate(request=0x0006400000015C1B, number_of_bytes_to_read=0)


def set_communication_parameters(instrument):
    instrument.serial.baudrate = BAUDRATE #globally defined
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = TIMEOUT #globally defined
    close_port_after_each_call: bool = False #sometimes windows might require this to be true.


def turn_relay_on(instrument, relay_register):
    instrument.write_register(relay_register, ON, functioncode=WRITE_RELAY)
    print("Relay turned on.")

def turn_relay_off(instrument, relay_register):
    instrument.write_register(relay_register, OFF, functioncode=WRITE_RELAY)
    print("Relay turned off.")


#Defining states
ON = 1
OFF = 0 

#function code variables
READ_STATUS = 1
READ_DEVICE_ADDRESS_AND_VERSION = 3 
WRITE_RELAY = 5
SET_ADDRESS_AND_BAUDRATE = 6
WRITE_ALL_RELAYS = int(0x0F)

# Define the general communication variables
BAUDRATE = 9600
TIMEOUT = 0.2 # seconds

#Define the Modbus slave address and port
port_name = '/dev/ttyUSB0'  # Change this to your specific port
device_address = 1 #0x01-0xFF for device address
set_device_address(port_name)

# Create a Modbus motor_relay_controller instance
motor_relay_controller = minimalmodbus.Instrument(port_name, device_address)
set_communication_parameters(motor_relay_controller, BAUDRATE, TIMEOUT)

# Define Modbus register addresses for relay control
left_lift_motor_register = 1  #0x00 - 0x001F, Assuming the relay is controlled by a single register


# Example usage:
turn_relay_on(motor_relay_controller, left_lift_motor_register)   # Turn the relay on
# Do something while the relay is on...
turn_relay_off(motor_relay_controller, left_lift_motor_register)  # Turn the relay off
