#About 75% of this code is nearly copied and pasted from a youtube
#tutorial; I wrote some top level functions that utilise these lower
#helper functions, such as compileData() and correctValues()


#I personally don't even know what a lot of the code does, all I know
#is that it outputs certain x and y gyroscope values
#Here's the link to the website where I got parts of this code:
#http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html


import smbus
import math

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

#findx the arc tangent of the x with the hypotoneuse
#to measure the actual angle of the sensor

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

#similarly, this does the same, only replacing the
#x and y values so that it measures the x axis angle

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68    # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

#tbis is the code that I wrote myself, which is the method that I'm using
#in the server.py

def compileData():
    data = ""
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)
    # print(gyro_zout + 150)

    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
    
    #16384 is a magic number, and it deals with the angular acceleration 
    #of the sensor. 

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    data = [-get_x_rotation(accel_xout_scaled, 
        accel_yout_scaled, accel_zout_scaled)]
    data += [-get_y_rotation(accel_xout_scaled, 
        accel_yout_scaled, accel_zout_scaled)]
    data += [gyro_zout - 150]

    return data




