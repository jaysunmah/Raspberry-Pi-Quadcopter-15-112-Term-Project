
import socket
from _thread import *
from queue import Queue
import datetime
import tkinter
import RPi.GPIO as GPIO
import time
from mpu import compileData

####################################
# server setup (sets up the server variables)
####################################


HOST = '128.237.238.152'
PORT = 21127
BACKLOG = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)#number of ppl that the server waits for before it starts
print("looking for connection")

clientList = []

####################################
# Motor Setup
####################################

#these terms refer to certain pin outputs on the raspberry pi
#the pins are hooked up to certain sensors which relay information
#to the pi

AIL = 15 #BCM: 22
ELE = 16 #BCM: 23
THR = 18 #BCM: 24 
RUD = 22 #BCM: 25
AUX = 24
LED = 26 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(AIL, GPIO.OUT)
GPIO.setup(ELE, GPIO.OUT)
GPIO.setup(THR, GPIO.OUT)
GPIO.setup(RUD, GPIO.OUT)
GPIO.setup(AUX, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)

#typical outputs are registed with digital outputs, which
#means they can either be 0 or 1, but now we will
#initialize them to input analog outputs, which ranges from
#values 0-255

ail = GPIO.PWM(AIL,100)
ail.start(1)

ele = GPIO.PWM(ELE,100)
ele.start(1)

thr = GPIO.PWM(THR,100)
thr.start(1)

rud = GPIO.PWM(RUD,100)
rud.start(1)

aux = GPIO.PWM(AUX,100)
aux.start(1)

time.sleep(0.1)

#These are magic numbers that I managed to find after alot of data testing
#these are the resting values where the motors won't run. 

ailPWM = 7.1	
elePWM = 7.1
thrPWM = 5.3
rudPWM = 7.1
auxPWMOn = 8
auxPWMOff = 6

maxPWM = 9.29 #this is 100%
minPWM = 5.3
restPWM = 7.1
thrIdle = 5.1

#the PWM's have a frequency of 50 hz, which is
#specific 

ail.ChangeFrequency(50)
ele.ChangeFrequency(50)
thr.ChangeFrequency(50)
rud.ChangeFrequency(50)
aux.ChangeFrequency(50)

ail.ChangeDutyCycle(ailPWM)
ele.ChangeDutyCycle(elePWM)
thr.ChangeDutyCycle(thrPWM)
rud.ChangeDutyCycle(rudPWM)
aux.ChangeDutyCycle(auxPWMOn)

####################################
# Ultrasonic Sensors setup
####################################

#sets up the ultrasonic sensors

# TRIG = 11 #18
# ECHO = 12 #17
TRIG = 13
ECHO = 7

GPIO.setup(TRIG, GPIO.OUT)
GPIO.output(TRIG, 0)
GPIO.setup(ECHO, GPIO.IN)

#this is the initial starting position of the copter. I implement this
#because the gyroscope doesn't read the rest position as perfectly 0,0
#so this basically can account for any slight error in the gyro readings

startingGyroValues = compileData()
startingX = startingGyroValues[0]
startingY = startingGyroValues[1]
startingYaw = startingGyroValues[2]
print('start', startingX, startingY)


####################################
# Initializing global data structures
####################################

keyInputs = {"w": False, "s": False, "d": False, "a": False, 
"u":False, "e":False, "r": False, "l": False, "g": True}

msg = {"distance": 0, "ail": 0, "ele": 0, "thr": 0, "rud": 0, "gyroX": 0, 
"gyroY": 0, "yaw":0}

isArming = False

####################################
# Handles commands
####################################

#constantly checks for new messages to be sent/relayed
#takes the message and adds it to the queue, which then
#gets sent to everyone connected to the server

def handleClient(client, serverChannel):
	global keyInputs
	while True:
		msg = client.recv(1000).decode('UTF-8')
		computeKeys(msg, keyInputs)

def computeMessage(serverChannel):
	global keyInputs, thr, thrPWM, ail, ailPWM, restPWM, isArming
	localMaxPWM = 7.8
	localMinPWM = 6.4
	rudMin = 6.8
	rudMax = 7.4
	while True:
		if keyInputs['u']:
			if thrPWM <= 6.5: thrPWM += 0.03
			thr.ChangeDutyCycle(thrPWM)
			print(thrPWM)
		elif keyInputs['e']: #e stands for down
			if keyInputs['g']: #g stands for grounded
				if thrPWM >= 5.3: thrPWM -= 0.03
				thr.ChangeDutyCycle(thrPWM)
				print(thrPWM)

		if keyInputs['d']:
			turnRight(localMaxPWM, localMinPWM)

		elif keyInputs['a']:
			turnLeft(localMaxPWM, localMinPWM)

		elif not (keyInputs['d'] and keyInputs['a']):
			selfLevel(restPWM)

		if keyInputs['l']:
			yawRight(rudMin)

		elif keyInputs['r']:
			yawLeft(rudMax)

		elif not (keyInputs['l'] and keyInputs['r']):
			if not isArming:
				yawStabilize(restPWM)

		time.sleep(0.01)

#this will tilt the quad to the right.

def turnRight(max,min):
	global ail, ailPWM
	error = max - ailPWM
	ailPWM += error * 0.04
	# print(ailPWM)
	ail.ChangeDutyCycle(ailPWM)

#this will tilt the quad to the left

def turnLeft(max, min):
	global ail, ailPWM
	error = min - ailPWM
	ailPWM += error * 0.04
	# print(ailPWM)
	ail.ChangeDutyCycle(ailPWM)

#this will smoothly reset the x axis tilt of the quad.

def selfLevel(rest):
	global ail, ailPWM
	error = rest - ailPWM
	ailPWM += error * 0.04
	ail.ChangeDutyCycle(ailPWM)

#this will smoothly turn the quad to the left

def yawLeft(min):
	global rud, rudPWM
	error = min - rudPWM
	rudPWM += error * 0.05
	rud.ChangeDutyCycle(rudPWM)

#this will smoothly turn the quad to the right

def yawRight(max):
	global rud, rudPWM
	error = max - rudPWM
	rudPWM += error * 0.05
	rud.ChangeDutyCycle(rudPWM)

#this will reset the yaw back to "rest", or the pwm value of 7.1
#This occurs when there is no user input, so the quad will naturally
#restabilize

def yawStabilize(rest):
	global rud, rudPWM
	error = rest - rudPWM
	rudPWM += error * 0.05
	rud.ChangeDutyCycle(rudPWM)	

#this will evaluate the keyInputs and set specific values or perform various
#tasks bsed on what key is inputted. 

def computeKeys(msg, keyInputs):
	for val in msg:
		if val == '1':
			keyInputs['g'] = True
		elif val == '0':
			keyInputs['g'] = False
		elif val == '8':
			armCopter()
		elif val == '9':
			disArmCopter()
		else:
			keyInputs[val] = not keyInputs[val]

#the quadcopter has a "safe" setting, like the safety on a gun
#when initially turned on, the copter will be on safe mode
#doing this process will arm the copter

def armCopter():
	global rud, rudPWM, thr, thrPWM, restPWM, thrIdle, isArming
	isArming = True
	rudPWM = restPWM
	rud.ChangeDutyCycle(rudPWM)
	thrPWM = thrIdle
	thr.ChangeDutyCycle(thrPWM)
	time.sleep(0.1)
	while rudPWM > restPWM - 1:
		rudPWM -= 0.1
		rud.ChangeDutyCycle(rudPWM)
		time.sleep(0.05)
	time.sleep(2)
	while rudPWM < 7.1:
		rudPWM += 0.1
		rud.ChangeDutyCycle(rudPWM)
		time.sleep(0.05)
	isArming = False

#this disarms the copter

def disArmCopter():
	global rud, rudPWM, thr, thrPWM, restPWM, thrIdle, isArming
	isArming = True
	rudPWM = restPWM
	rud.ChangeDutyCycle(rudPWM)
	thrPWM = thrIdle
	thr.ChangeDutyCycle(thrPWM)
	time.sleep(0.2)
	while rudPWM < restPWM + 1:
		rudPWM += 0.1
		rud.ChangeDutyCycle(rudPWM)
		time.sleep(0.05)
	time.sleep(2)
	while rudPWM > 7.1:
		rudPWM -= 0.1
		rud.ChangeDutyCycle(rudPWM)
		time.sleep(0.05)
	isArming = False

#this is constantly run to check the queue for new messages, if there is, 
#it'll put() it in the queue



####################################
# Threading scripts
####################################

#sends back to the user whatever data is in the serverChannel queue

def serverThread(clientList, serverChannel):
	while True:
		msg = serverChannel.get(True, None)
		for client in clientList:
			client.send(bytes(msg, "UTF-8"))


serverChannel = Queue(100)

#constantly checks for new server messages
start_new_thread(serverThread, (clientList, serverChannel))


#measures the distance of the signals that the ultrasonic sensors pick up
#the 1700 is the speed in which radio waves travel; essentially this is
#converting pulse widths of the ultra sonic waves and computing
#how far the waves had to travel

def measureDistance():
	constant = 17000
	GPIO.output(TRIG, 1)
	time.sleep(0.00001)
	GPIO.output(TRIG, 0)
	while GPIO.input(ECHO) == 0:
		pass
	start = time.time()
	while GPIO.input(ECHO) == 1:
		pass
	stop = time.time()
	return ((stop - start) * constant)

#this takes three different outputs and averages them; this makes it more
#accurate

def measureAverage():
	dist1 = measureDistance()
	time.sleep(0.1)
	dist2 = measureDistance()
	time.sleep(0.1)
	dist3 = measureDistance()
	totalDistance = (dist1 + dist2 + dist3) / 3
	return totalDistance

#this method will constantly put the global dictionary "msg" in the server
#channel. It doesn't care what state the dictionary is at, it will 
#simply send whatever is in it.

def sendData(serverChannel):
	global msg
	while True:
		serverChannel.put(repr(msg))	

#this will constantly update the "distance" key in the dictionary. 

def addDistance(serverChannel):
	global msg
	while True:
		msg["distance"] = measureAverage()

#this will constantly update the gyroscope and yaw data 

def addGyro(serverChannel):
	global msg, startingX, startingY
	while True:
		dataVals = compileData()
		# print(dataVals)
		x = float(dataVals[0])
		y = float(dataVals[1])
		yaw = float(dataVals[2])
		msg["gyroX"] = x # - startingX
		msg["gyroY"] = y #- startingY
		msg["yaw"] = yaw - startingYaw
		# time.sleep(0.1)

#this will constantly update the motor values to the dictionary

def addMotorVals(serverChannel):
	global msg, ailPWM, elePWM, thrPWM, rudPWM
	while True:
		msg["ail"] = ailPWM
		msg["ele"] = elePWM
		msg["thr"] = thrPWM
		msg["rud"] = rudPWM


#resets the throttle pwm to zero once the client list is zero
#this is a safety mechanism so that once the client disconnects, 
#the throttle will shut down.

def resetMotors():
	global clientList
	while True:
		if len(clientList) < 1:
			print('nobodys here')
			thrPWM = 0

#each of these threads will update the dictionary with its respective
#attributes

start_new_thread(addDistance, (serverChannel,))
start_new_thread(addGyro, (serverChannel,))
start_new_thread(addMotorVals, (serverChannel,))
start_new_thread(sendData, (serverChannel,))
start_new_thread(computeMessage, (serverChannel,))


#this handles the client.

while True:
	client, address = server.accept()
	clientList.append(client)
	print("connection recieved")
	start_new_thread(handleClient, (client,serverChannel)) 






