#Jason Ma jasonm2 section P


from math import pi, sin, cos, radians
import socket
import time
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
import sys
from direct.stdpy import thread
from Queue import Queue
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, TransparencyAttrib
import datetime
from direct.gui.DirectGui import *
import os
from panda3d.core import *
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import loadPrcFileData

loadPrcFileData("", "window-title Pycopter")
loadPrcFileData("", "win-size 1660 990")
loadPrcFileData("", "win-origin 0 0")

####################################
# server setup (sets up the client IP address variables)
####################################

HOST = '128.237.238.152'
# HOST = ''
PORT = 21127
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST, PORT))
print("connected to server")

####################################
# panda world setup
####################################

#Fair warning: None of the models in here were made by me
#There's a public library of downloadable models provided by
#Panda 3D


class MyApp(ShowBase):
	def __init__(self, server):
		ShowBase.__init__(self)

		#the way the user interface can read held down buttons is by
		#setting the button to be true when it's pressed down, and then
		#it sets it back to false when it's released
		#I have a constant while loop that'll simply read the key dictionary
		#and act whenever one of the values reads True, or in this case 1
		self.keys = {"w": 0, "s": 0, "d": 0, "a":0,"u":0, "e":0,"r": 0,"l": 0}
		self.initPart2()

	#part 2 of the init, the first one got taken up by alot of comments

	def initPart2(self):
		#assigns all of the variables needed in the class
		self.defineVariables()

		self.loadEnvironments()
		
		self.camera.setPos(29,-20,2)
		# self.camera.setHpr(-123.333, 0, 0)
		self.loadModels()

		self.initializeKeys1()
		self.initializeKeys2()

		self.startThreads()

	#these are the data variables that are being sent by the server. so far,
	#I haven't displayed any of these variables, as I've noticed they cause
	#a fair amount of lag/delay, but I am implementing the gyroscope values

	def defineVariables(self):
		self.initializePiVariables()
		self.initializePandaVarialbes()


	def initializePiVariables(self):
		self.ail = 0
		self.ele = 0
		self.thr = 0
		self.rud = 0
		self.gyroX = 0
		self.gyroY = 0
		self.yaw = 0


	#initializing more global variables
	def initializePandaVarialbes(self):	
		self.cameraSpeed = 0.5
		self.moveSpeed = 0.2
		self.quadDistance = 15
		self.noYawInput = True
		self.throttlePower = "o "
		self.dX = 0
		self.dTheta = 0
		self.isMoving = False
		self.dictOfRecords = dict()
		self.keysPressedDown = set()
		self.username = ""
		self.initializePandaVariablesPart2()

	def initializePandaVariablesPart2(self):
		self.timer = 0.00
		self.timerRunning = False
		self.timerLastModified = self.getTime()
		self.initializePromptTextPart1()
		self.initializePromptTextPart2()
		self.initializePressedDownKeyText()	
		self.toggleLiftOff = True
		self.listOfModelPaths= ['models/fighter/fighter', 
		'models/boeing/boeing707', 'models/r2d2/r2d2', 
		'models/blimp/blimp', 'models/seeker/seeker', 
		'models/jeep/jeep']
		self.modelIndex = 0		

	def initializePromptTextPart1(self):
		self.timerText = TextNode('timer')
		self.timerText.setText("Time:" + "0" + str(self.timer))
		self.timerText.setShadow(0.05, 0.05)
		self.timerTextNodePath = aspect2d.attachNewNode(self.timerText)
		self.timerTextNodePath.setScale(0.07)
		self.timerTextNodePath.setPos(1.2,0,0.9)

		self.saveTimeText = TextNode('would you like to save?')
		self.saveTimeText.setText('')#
		self.saveTimeText.setShadow(0.05, 0.05)
		self.saveTimeTextNodePath = aspect2d.attachNewNode(self.saveTimeText)
		self.saveTimeTextNodePath.setScale(0.07)
		self.saveTimeTextNodePath.setPos(1.1, 0, 0.8)


	def initializePromptTextPart2(self):
		self.thrStatus = ""
		self.loadModelsText = "Select your model!\nPress [B] to go back!"
		line1 = "Press [H] for Help!\n"
		line2 = "Press [L] to load high scores!\n"
		line3 = "Press [G] to change skins!\n\n"
		line4 = "Throttle Status: " + self.thrStatus
		self.helperText = line1 + line2 + line3 + line4

		self.helpText = TextNode('help')
		self.helpText.setText(self.helperText)
		self.helpTextNodePath = aspect2d.attachNewNode(self.helpText)
		self.helpTextNodePath.setScale(0.07)
		self.helpTextNodePath.setPos(-1.5,0,0.9)
		self.helpText.setShadow(0.05, 0.05)
		self.initializeUserInputText()

	def initializeUserInputText(self):
		self.loadModelText = TextNode('load models')
		self.loadModelText.setText("")
		self.loadModelTextNodePath = aspect2d.attachNewNode(self.loadModelText)
		self.loadModelTextNodePath.setScale(0.07)
		self.loadModelTextNodePath.setPos(-1.5,0,0.9)
		self.loadModelText.setShadow(0.05, 0.05)

		self.defaultText = "type in your name!"
		self.textObject=OnscreenText(text=self.defaultText,pos = (1.25,-0.95), 
		scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)
		self.nameEntry=DirectEntry(text = "",scale=.05,command=self.setText,
		initialText="Type Something", numLines = 2,focus=1,
		focusInCommand=self.clearText)
		self.nameEntry.setPos(1.05,0,-0.8)

	def initializePressedDownKeyText(self):
		self.initializePressedDownKeysPart1()
		self.initializePressedDownKeysPart2()
		self.initializePressedDownKeysPart3()
		self.initializePressedDownKeysPart4()

	def initializePressedDownKeysPart1(self):
		self.wText = TextNode('w')
		self.wText.setText("w")
		self.wText.setShadow(0.05, 0.05)
		self.wTextNodePath = aspect2d.attachNewNode(self.wText)
		self.wTextNodePath.setScale(0.07)
		self.wTextNodePath.setPos(-1.6,0,-0.75)

		self.sText = TextNode('s')
		self.sText.setText("s")
		self.sText.setShadow(0.05, 0.05)
		self.sTextNodePath = aspect2d.attachNewNode(self.sText)
		self.sTextNodePath.setScale(0.07)
		self.sTextNodePath.setPos(-1.35,0,-0.75)

	def initializePressedDownKeysPart2(self):
		self.aText = TextNode('a')
		self.aText.setText("a")
		self.aText.setShadow(0.05, 0.05)
		self.aTextNodePath = aspect2d.attachNewNode(self.aText)
		self.aTextNodePath.setScale(0.07)
		self.aTextNodePath.setPos(-1.1,0,-0.75)	

		self.dText = TextNode('d')
		self.dText.setText("d")
		self.dText.setShadow(0.05, 0.05)
		self.dTextNodePath = aspect2d.attachNewNode(self.dText)
		self.dTextNodePath.setScale(0.07)
		self.dTextNodePath.setPos(-0.85,0,-0.75)

	def initializePressedDownKeysPart3(self):
		self.upText = TextNode('Up')
		self.upText.setText("Up")
		self.upText.setShadow(0.05, 0.05)
		self.upTextNodePath = aspect2d.attachNewNode(self.upText)
		self.upTextNodePath.setScale(0.07)
		self.upTextNodePath.setPos(-1.6,0,-0.85)

		self.downText = TextNode('Down')
		self.downText.setText("Down")
		self.downText.setShadow(0.05, 0.05)
		self.downTextNodePath = aspect2d.attachNewNode(self.downText)
		self.downTextNodePath.setScale(0.07)
		self.downTextNodePath.setPos(-1.35,0,-0.85)

	def initializePressedDownKeysPart4(self):
		self.rightText = TextNode('Left')
		self.rightText.setText("Left")
		self.rightText.setShadow(0.05, 0.05)
		self.rightTextNodePath = aspect2d.attachNewNode(self.rightText)
		self.rightTextNodePath.setScale(0.07)
		self.rightTextNodePath.setPos(-1.1,0,-0.85)	

		self.leftText = TextNode('Right')
		self.leftText.setText("Right")
		self.leftText.setShadow(0.05, 0.05)
		self.leftTextNodePath = aspect2d.attachNewNode(self.leftText)
		self.leftTextNodePath.setScale(0.07)
		self.leftTextNodePath.setPos(-0.85,0,-0.85)		

	def setText(self, textEntered):
		self.textObject.setText(textEntered)
		self.username = self.textObject.getText()

		#clear the text
	def clearText(self):
		self.nameEntry.enterText('')


	#returns the date for the timer method
	def getTime(self):
		time = str(datetime.datetime.now())
		return (time[11:]) 

	#this returns the string date in a format that is compatibile for
	#the save and load files method

	def getDateTime(self):
		time = str(datetime.datetime.now())
		return time[:10] + "," + time[11:19]

	#loads the environments. So far I have the sky model and a jungle 
	#environment.

	def loadEnvironments(self):
		self.disableMouse()

		self.environ = self.loader.loadModel("models/sky/blue-sky-sphere")
		self.environ.reparentTo(self.render)
		self.environ.setScale(0.25, 0.25, 0.25)
		self.environ.setPos(0, 0, 0)

		self.environ1 = self.loader.loadModel("models/course/course1")
		self.environ1.reparentTo(self.render)
		self.environ1.setScale(2.0, 2.0, 2.0)
		self.environ1.setPos(0, 0, 0)
		self.environ1.setHpr(123,0,0)


	#this method will load all of the models. So far I only have two, but
	#I intend on adding more later

	def loadModels(self):
		self.loadPanda()
		self.loadQuad()

	#this method loads the panda model. It has a walk animation, as well
	#as a movement path. I modified parts of this code while following a panda3D tutorial:
	#https://www.panda3d.org/manual/index.php/Loading_and_Animating_the_Panda_Model

	def loadPanda(self):
		self.pandaActor = Actor("models/panda-model", 
			{"walk": "models/panda-walk4"})
		self.pandaActor.setScale(0.005, 0.005, 0.005)
		self.pandaActor.reparentTo(self.render)
		self.pandaActor.setHpr(90,0,0)
		# Loop its animation.
		self.pandaActor.loop("walk")
		# Create the four lerp intervals needed for the panda to move
		pandaPosInterval1 = self.pandaActor.posInterval(13, Point3(-33, 0, -1),
													startPos=Point3(-41, 0,-1))
		pandaPosInterval2 = self.pandaActor.posInterval(13, Point3(-41, 0, -1),
													startPos=Point3(-33, 0, -1))
		pandaHprInterval1 = self.pandaActor.hprInterval(3, Point3(-90, 0, 0),
													startHpr=Point3(90, 0, 0))
		pandaHprInterval2 = self.pandaActor.hprInterval(3, Point3(90, 0, 0),
													startHpr=Point3(-90, 0, 0))
		# Create and play the sequence that coordinates the intervals.
		self.pandaPace = Sequence(pandaPosInterval1,pandaHprInterval1, 
			pandaPosInterval2, pandaHprInterval2, name="pandaPace")
		self.pandaPace.loop()

	#this will load the quad model. As of right now, it is only a demo model
	#but I plan on making my own quad model later

	def loadQuad(self):
		# Load and transform the panda actor.
		self.quad = loader.loadModel('models/fighter/fighter')
		self.quad.reparentTo(self.render)
		self.quad.setScale(0.15, 0.15, 0.15)
		self.quad.setPos(self.camera, 0, self.quadDistance,-2)
		self.quad.setHpr(self.camera, 0,0,0)

	#sets the keyinputs. I split it into two methods to make it more 
	#readable
	#the way the key inputs are read in panda is pressing the key down
	#generates one pulse, and then releasing the button generates another
	#pulse. Each time a pulse is fired, panda will set the value of a key
	#to be either True (when it's pressed down) or False (when it's not 
	#pressed down). 

	def initializeKeys1(self):
		self.accept("escape", sys.exit)

		self.accept("arrow_up", self.setKey, ["u", 1, server])
		self.accept("arrow_up-up", self.setKey, ["u", 0, server])

		self.accept("arrow_down", self.setKey, ["e", 1, server])
		self.accept("arrow_down-up", self.setKey, ["e", 0, server])

		self.accept("arrow_right", self.setKey, ["l", 1, server])
		self.accept("arrow_right-up", self.setKey, ["l", 0, server])

		self.accept("arrow_left", self.setKey, ["r", 1, server])
		self.accept("arrow_left-up", self.setKey, ["r", 0, server])


		self.accept('g', self.pickModel, [])
	#part two of initialize keys

	def initializeKeys2(self):
		self.accept("w", self.setKey, ["w", 1, server])
		self.accept("w-up", self.setKey, ["w", 0, server])
		self.accept("s", self.setKey, ["s", 1, server])
		self.accept("s-up", self.setKey, ["s", 0, server])
		self.accept("d", self.setKey, ["d", 1, server])
		self.accept("d-up", self.setKey, ["d", 0, server])
		self.accept("a", self.setKey, ["a", 1, server])
		self.accept("a-up", self.setKey, ["a", 0, server])
		self.accept('8', self.sendMsg, ['8', server]) #arm
		self.accept('9', self.sendMsg, ['9', server]) #disarm
		self.accept('l', self.displayHighScores, [])
		self.accept('p', self.startStopTimer, [])
		self.accept('h', self.getHelp, [])
		self.accept('b', self.returnToGame, [])
		self.accept('y', self.saveTime, [])
		self.accept('n', self.resetTime, [])

		self.accept('1', self.swapModel, [1])
		self.accept('2', self.swapModel, [2])
		self.accept('3', self.swapModel, [3])
		self.accept('4', self.swapModel, [4])
		self.accept('5', self.swapModel, [5])
		self.accept('6', self.swapModel, [6])

	#saves the times on a text file

	def swapModel(self, index):
		# self.modelIndex += 1
		# self.modelIndex = self.modelIndex % len(self.listOfModelPaths)
		index -= 1
		if index < len(self.listOfModelPaths):
			path = self.listOfModelPaths[index]
			self.quad.removeNode()
			self.quad = loader.loadModel(path)
			self.quad.reparentTo(self.render)
			scale = self.pickScale(path)
			self.quad.setScale(scale)
			self.quad.setPos(self.camera, 0, self.quadDistance,-2)
			self.quad.setHpr(self.camera, 0,0,0)

	#this is the overall method used to display the models when the [G]
	#button is pressed. I split it into a top down design so it is easier
	#to read

	def pickModel(self):
		self.loadPickModelPart1()
		self.loadPickModelPart2()
		self.loadPickModelPart3()
		self.loadPickModelTextPart1()
		self.loadPickModelTextPart2()
		self.loadPickModelTextPart3()

	#loads the Fighter and Boeing model

	def loadPickModelPart1(self):
		self.helpText.setText("")
		self.loadModelText.setText(self.loadModelsText)
		
		self.skin1 = self.loader.loadModel("models/fighter/fighter")
		self.skin1.reparentTo(self.render)
		self.skin1.setScale(0.1, 0.1, 0.1)
		self.skin1.setPos(self.camera, -4.5, self.quadDistance,2)
		self.skin1.setHpr(self.camera, 180, 0,0)

		self.skin2 = self.loader.loadModel("models/boeing/boeing707")
		self.skin2.reparentTo(self.render)
		self.skin2.setScale(0.08, 0.08, 0.08)
		self.skin2.setPos(self.camera, 0.5, self.quadDistance,2)
		self.skin2.setHpr(self.camera, 180, 0,0)

	#loads the R2D2 and blimp model

	def loadPickModelPart2(self):
		self.skin3 = self.loader.loadModel("models/r2d2/r2d2")
		self.skin3.reparentTo(self.render)
		self.skin3.setScale(0.5, 0.5, 0.5)
		self.skin3.setPos(self.camera, 4.5, self.quadDistance,2)
		self.skin3.setHpr(self.camera, 180, 0,0)

		self.skin4 = self.loader.loadModel("models/blimp/blimp")
		self.skin4.reparentTo(self.render)
		self.skin4.setScale(0.03, 0.03, 0.03)
		self.skin4.setPos(self.camera, -4.5, self.quadDistance,-0.5)
		self.skin4.setHpr(self.camera, 180, 0,0)

	#loads the seeker and jeep model

	def loadPickModelPart3(self):
		self.skin5 = self.loader.loadModel("models/seeker/seeker")
		self.skin5.reparentTo(self.render)
		self.skin5.setScale(0.8, 0.8, 0.8)
		self.skin5.setPos(self.camera, 0.5, self.quadDistance,-0.5)
		self.skin5.setHpr(self.camera, 180, 0,0)

		self.skin6 = self.loader.loadModel("models/jeep/jeep")
		self.skin6.reparentTo(self.render)
		self.skin6.setScale(0.17, 0.17, 0.17)
		self.skin6.setPos(self.camera, 4.5, self.quadDistance,-1.0)
		self.skin6.setHpr(self.camera, 0, 0,0)

	#loads label text for the figher and boeing

	def loadPickModelTextPart1(self):
		self.skin1Text = TextNode('skin1')
		self.skin1Text.setText("[1] - Fighter")
		self.skin1Text.setShadow(0.05, 0.05)
		self.skin1TextNodePath = aspect2d.attachNewNode(self.skin1Text)
		self.skin1TextNodePath.setScale(0.07)
		self.skin1TextNodePath.setPos(-1.3,0,0.3)	

		self.skin2Text = TextNode('skin2')
		self.skin2Text.setText("[2] - Boeing707")
		self.skin2Text.setShadow(0.05, 0.05)
		self.skin2TextNodePath = aspect2d.attachNewNode(self.skin2Text)
		self.skin2TextNodePath.setScale(0.07)
		self.skin2TextNodePath.setPos(-0.1,0,0.3)	

	#loads label text for R2D2 and the Blimp

	def loadPickModelTextPart2(self):

		self.skin3Text = TextNode('skin3')
		self.skin3Text.setText("[3] - R2D2")
		self.skin3Text.setShadow(0.05, 0.05)
		self.skin3TextNodePath = aspect2d.attachNewNode(self.skin3Text)
		self.skin3TextNodePath.setScale(0.07)
		self.skin3TextNodePath.setPos(1,0,0.3)	

		self.skin4Text = TextNode('skin4')
		self.skin4Text.setText("[4] - Blimp")
		self.skin4Text.setShadow(0.05, 0.05)
		self.skin4TextNodePath = aspect2d.attachNewNode(self.skin4Text)
		self.skin4TextNodePath.setScale(0.07)
		self.skin4TextNodePath.setPos(-1.3,0,-0.5)	

	#loads the label text for Seeker and Jeep

	def loadPickModelTextPart3(self):
		self.skin5Text = TextNode('skin5')
		self.skin5Text.setText("[5] - Seeker")
		self.skin5Text.setShadow(0.05, 0.05)
		self.skin5TextNodePath = aspect2d.attachNewNode(self.skin5Text)
		self.skin5TextNodePath.setScale(0.07)
		self.skin5TextNodePath.setPos(-0.1,0,-0.5)	

		self.skin6Text = TextNode('skin6')
		self.skin6Text.setText("[6] - Jeep")
		self.skin6Text.setShadow(0.05, 0.05)
		self.skin6TextNodePath = aspect2d.attachNewNode(self.skin6Text)
		self.skin6TextNodePath.setScale(0.07)
		self.skin6TextNodePath.setPos(1,0,-0.5)	

	#this is the overall method that will return how the model should
	#be sized. All of this is magic numbers, and I found them based on 
	#my personal preference to how the models should look aesthetically 

	def pickScale(self, path):
		if path == "models/fighter/fighter":
			return (0.15,0.15,0.15)
		elif path == "models/boeing/boeing707":
			return (0.1,0.1,0.1)
		elif path == "models/r2d2/r2d2":
			return (0.7,0.7,0.7)
		elif path == "models/blimp/blimp":
			return (0.05,0.05,0.05)
		elif path == "models/seeker/seeker":
			return (0.8,0.8,0.8)
		elif path == 'models/jeep/jeep':
			return (0.25,0.25,0.25)

	#This will save whatever time the user has, assuming the inputted
	#username isn't empty. It will save the data into a text file called
	#"Records"

	def saveTime(self):
		savedTime = self.timer
		if self.username != '':
			if (os.path.isfile('Records')):
				file = open('Records', "r")
				result = (self.username + "," + self.getDateTime() + "," 
					+ savedTime + "\n")
				stringOfRecords = file.read()
				stringOfRecords += result
				file = open('Records', "w")
				file.write(stringOfRecords)
			else:
				file = open('Records', "w")
				file.write(self.username + "," + self.getDateTime() + "," 
					+ savedTime + "\n")
		self.timerText.setText("Time: 00.0")
		self.timer = 0

	#this will reset the timerText to 0:00 and the 
	#timer variable back to zero.

	def resetTime(self):
		self.timerText.setText("Time: 00.0")
		self.timer = 0

	#this will reset the menu screen to the default display. I had to add
	#a try block to it just in case some of the models don't properly load
	#if they don't load, and you try to delete them, the program will crash

	def returnToGame(self):
		try:
			self.helpText.setText(self.helperText)
			self.loadModelText.setText("")
			self.skin1.removeNode()
			self.skin2.removeNode()
			self.skin3.removeNode()
			self.skin4.removeNode()
			self.skin5.removeNode()
			self.skin6.removeNode()
			self.skin1Text.setText("")
			self.skin2Text.setText("")
			self.skin3Text.setText("")
			self.skin4Text.setText("")
			self.skin5Text.setText("")
			self.skin6Text.setText("")
		except: pass

	#This is the help menu when [H] is pressed

	def getHelp(self):
		line1 = "Press [B] to go back\n"
		line2 = "[W] - Move forwards\n"
		line3 = "[S] - Move backwards\n"
		line4 = "[D] - Move right\n"
		line5 = "[A] - Move left\n"
		line6 = "[Right Arrow] - Rotate right\n"
		line7 = "[Left Arrow] - Rotate left\n"
		line8 = "[Up Arrow] - Move up\n"
		line9 = "[Down Arrow] - Move down\n"
		line10 = "[8] - Arm Copter\n"
		line11 = "[9] - Disarm Copter"
		self.helpText.setText(line1 + line2 + line3 + line4 + line5 + line6 
			+ line7 + line8 + line9 + line10 + line11)

	#opens up a file called "records" if it exists, and then proceeds to load
	#and read the data

	def displayHighScores(self):
		if (os.path.isfile('Records')):
			file = open('Records', 'r')
			stringRecords = file.read()
			stringRecords = stringRecords.split('\n')[:-1]
			self.dictOfRecords = dict()
			for person in stringRecords:
				person = person.split(',')
				key = person[0] #sets the key index to the person's name
				person = person[1:] #cuts the name part off now
				if key in self.dictOfRecords:
					self.dictOfRecords[key] += [person]
				else:
					self.dictOfRecords[key] = [person]
			self.organizeDictionaryOfRecords()

	#once the file has been read, this method will decipher the dictionary of
	#people with their lists of times. It will then sort them in descending order
	#this is all destructive, by the way.

	def organizeDictionaryOfRecords(self):
		for person in self.dictOfRecords: #jason, Jason
			if len(self.dictOfRecords[person]) > 1:
				self.sortTimes(self.dictOfRecords[person])
		line1 = "Record Board: (date, datetime, time)\n"
		line2 = "Press [B] to go back\n"
		sortedStringOfRecords = line1 + line2
		for person in self.dictOfRecords:
			sortedStringOfRecords += person + ":\n"
			for stats in self.dictOfRecords[person]:
				for stat in stats:
					sortedStringOfRecords += stat + "\t\t"
				sortedStringOfRecords += "\n"
			sortedStringOfRecords += "\n"
		self.helpText.setText(sortedStringOfRecords)


	#this is a variation of the merge method in merge sort, modified to sort
	#lists of lists.

	def merge(self, l, s1, s2, end):
		index1 = s1
		index2 = s2
		length = end - s1
		aux = [None] * length
		for i in range(length):
			if (index1 == s2) or ((index2 != end) and 
	(self.convertToSeconds(l[index1][2])>self.convertToSeconds(l[index2][2]))):
				aux[i] = l[index2]
				index2 += 1
			else:
				aux[i] = l[index1]
				index1 += 1
		for i in range(s1, end):
			l[i] = aux[i - s1]

	#when I was comparing times, I forgot I also had to compare times when it
	#read like 1:02, and I was no longer just comparing seconds. So I had to 
	#write a method that will conver the time first to seconds before it 
	#gets compared.

	def convertToSeconds(self, time):
		if ":" in time:
			minutes = float(time[:time.index(":")])
			seconds = minutes * 60 + float(time[time.index(":") + 1:])
			return seconds
		return float(time)

	#this is parent the "mergeSort", modified to sort the list of lists

	def sortTimes(self, listOfTimes):
		n = len(listOfTimes)
		step = 1
		while (step < n):
			for s1 in range(0, n, 2 * step):
				s2 = min(s1 + step, n)
				end = min(s1 + 2 * step, n)
				self.merge(listOfTimes, s1, s2, end)
			step *= 2

	#toggles the self.timerRunning variable, and sets the timerBegin variable
	#if the timer just started

	def startStopTimer(self):
		if not self.timerRunning:
			self.timerBegin = self.getTime()
		self.timerRunning = not self.timerRunning

	#to make things more organized, I combined all of the threaded methods
	#here, so I can modify/add more in the future if needed

	def startThreads(self):
		thread.start_new_thread(self.rotateQuad, (server,))
		thread.start_new_thread(self.handleServerMsg, (server,))
		thread.start_new_thread(self.moveCamera, (server,))	
		thread.start_new_thread(self.spinQuad, (server, ))
		thread.start_new_thread(self.evaluateHits, (server, ))	
		thread.start_new_thread(self.runTimer, (server, ))

	#this method is only used for button actions that don't require buttons
	#to be held down. For example, pressing 8 and 9 will arm and disarm the
	#copter, and holding them down won't do anything. So sendMsg will basically
	#send a single pulse to the server, which will know what to do for 
	#specific single pulses.

	def sendMsg(self, msg, server):
		server.send(bytes(msg))

	#evalKey is only used by the down button. It essentially determines
	#if the copter is on the ground before it tries to lower the quad's
	#actual throttle. I do this to simulate more of a "real" effect, where
	#the quad in real life will only shut down once the quad in the
	#simulation has actually touched the ground.

	def evalKey(self, key, val, server):
		if self.quad.getZ() < 0 and not self.keys['e']:
			self.setKey(key, val, server)
		else:
			self.keys[key] = val

	#set key will merely change the dictionary of keys to whatever value
	#it is inputed. Then, it will send a pulse to the server, which will
	#read it as a double pulse and modify its own variables accordingly. 

	def setKey(self, key, val, server):
		self.keys[key] = val
		server.send(bytes(key))

		for key in self.keys:
			if self.keys[key]:
				self.keysPressedDown.add(key)
			else:
				if key in self.keysPressedDown:
					self.keysPressedDown.remove(key)

		# self.updatePressedDownKeys()
		self.setPressedDownKeys()

	def setPressedDownKeys(self):
		if self.keys['w']: self.wText.setText('w')
		else: self.wText.setText('')
		if self.keys['a']: self.aText.setText('a')
		else: self.aText.setText('')
		if self.keys['s']: self.sText.setText('s')
		else: self.sText.setText('')
		if self.keys['d']: self.dText.setText('d')
		else: self.dText.setText('')
		if self.keys['u']: self.upText.setText('Up')
		else: self.upText.setText('')
		if self.keys['e']: self.downText.setText('Down')
		else: self.downText.setText('')
		if self.keys['l']: self.leftText.setText('Right')
		else: self.leftText.setText('')
		if self.keys['r']: self.rightText.setText('Left')
		else: self.rightText.setText('')


	# def updatePressedDownKeys(self): pass


	def moveCamera(self, server):
		while True:
			try:
				if self.quad.getZ() < 0:
					server.send(bytes('1')) #ground
				else:
					server.send(bytes('0')) #air
				if self.quad.getZ() > 0:	
					if self.keys["w"]:
						self.camera.setPos(self.camera, 0, self.moveSpeed, 0)
						self.quad.setPos(self.camera, 0, self.quadDistance, -2)
						self.tiltForward()
	
					elif self.keys["s"]:
						self.camera.setPos(self.camera, 0, -self.moveSpeed, 0)
						self.quad.setPos(self.camera, 0, self.quadDistance, -2)
						self.tiltBackward()
					else:
						self.pitchSelfLevel()
	
					if self.keys["d"]:
						self.quad.setHpr(self.quad, 0, 0, pi / 8)
						self.isMoving = True
	
					elif self.keys["a"]:
						self.quad.setHpr(self.quad, 0, 0, -pi / 8)
						self.isMoving = True				
	
					elif not (self.keys['d'] and self.keys['a']):
						self.isMoving = False
						self.driftStabilize()
					
				self.moveCameraPart2(server)
			except: pass

	def moveCameraPart2(self, server):
		if self.keys["u"]:
			if self.thr >= 6.4:
				if self.toggleLiftOff:
					self.thrStatus = "Take off!"
					line1 = "Press [H] for Help!\n"
					line2 = "Press [L] to load high scores!\n"
					line3 = "Press [G] to change skins!\n\n"
					line4 = "Throttle Status: " + self.thrStatus
					self.helpText.setText(line1 + line2 + line3 + line4)
					self.toggleLiftOff = False

				self.camera.setPos(self.camera, 0, 0, self.moveSpeed / 2)
				self.quad.setPos(self.camera, 0, self.quadDistance, -2)
			else:
				self.thrStatus = "Starting up motors..."
				line1 = "Press [H] for Help!\n"
				line2 = "Press [L] to load high scores!\n"
				line3 = "Press [G] to change skins!\n\n"
				line4 = "Throttle Status: " + self.thrStatus
				self.helpText.setText(line1 + line2 + line3 + line4)

		self.moveCameraPart3(server)


		#this is the down arrow, but I had no other key to set it to : /
		#the keys sent must be of one character long because thats how
		#the server can read messages (it goes through each message
		#character by character)
		
	def moveCameraPart3(self, server):
		if self.keys["e"]: 
			if self.quad.getZ() > -0.01:
				self.camera.setPos(self.camera, 0, 0, -self.moveSpeed / 2)
				self.quad.setPos(self.camera, 0, self.quadDistance, -2)
			elif self.thr < 5.3:
				self.thrStatus = "Landed!"
				line1 = "Press [H] for Help!\n"
				line2 = "Press [L] to load high scores!\n"
				line3 = "Press [G] to change skins!\n\n"
				line4 = "Throttle Status: " + self.thrStatus
				self.helpText.setText(line1 + line2 + line3 + line4)

			else:
				self.toggleLiftOff = True
				self.thrStatus = "Landing..."
				line1 = "Press [H] for Help!\n"
				line2 = "Press [L] to load high scores!\n"
				line3 = "Press [G] to change skins!\n\n"
				line4 = "Throttle Status: " + self.thrStatus
				self.helpText.setText(line1 + line2 + line3 + line4)
		self.moveCameraPart4(server)

	def moveCameraPart4(self, server):
		if self.keys["r"]:
			self.noYawInput = False
		elif self.keys['l']:
			self.noYawInput = False
		elif not (self.keys["r"] and self.keys["l"]):
			self.yawSelfLevel()

		time.sleep(0.01)


		#this method if replacing the if statement above will manually control
		#the rotation of the quad regardless of the overall orientation of
		#the physical quad. I'm going to leave the code here just in case
		#I ever need to manually control the quad in the future.

		# if self.keys["l"]:
		# 	self.camera.setHpr(self.camera, -self.cameraSpeed / 2, 0,0)
		# 	deltaX = - (cos(radians(90 - self.cameraSpeed)) * 
		# 		self.quadDistance) * cos(radians(self.cameraSpeed))
		# 	deltaY = (cos(radians(90 - self.cameraSpeed)) * 
		# 		self.quadDistance) * sin(radians(self.cameraSpeed))
		# 	self.camera.setPos(self.camera, deltaX, deltaY, 0)
		# 	self.quad.setHpr(self.camera, 0,self.quad.getP(),self.quad.getR())

		# elif self.keys["r"]:
		# 	self.camera.setHpr(self.camera, self.cameraSpeed / 2, 0, 0)
		# 	deltaX = (cos(radians(90 - self.cameraSpeed)) * 
		# 		self.quadDistance) * cos(radians(self.cameraSpeed))
		# 	deltaY = (cos(radians(90 - self.cameraSpeed)) * 
		# 		self.quadDistance) * sin(radians(self.cameraSpeed))
		# 	self.camera.setPos(self.camera, deltaX, deltaY, 0)
		# 	self.quad.setHpr(self.camera,0,self.quad.getP(),self.quad.getR())



	def tiltForward(self):
		desiredVal = -15
		error = desiredVal - self.quad.getP()
		self.quad.setHpr(self.quad, 0, error * 0.05, 0)

	def tiltBackward(self):
		desiredVal = 15
		error = desiredVal - self.quad.getP()
		self.quad.setHpr(self.quad, 0, error * 0.05, 0)

	def pitchSelfLevel(self):
		desiredVal = 0
		error = desiredVal - self.quad.getP()
		self.quad.setHpr(self.quad, 0, error * 0.05, 0)

	#currently working on this aspect of the simulation: the quad is noted
	#to have random bursts of movement which causes a lot of jitter; trying
	#to see how I can manage to stabilize the motion

	def rotateQuad(self, server): #this rotates roll
		while True:
			try:
				self.updateSaveTimer()
				#this will rotate the quad
				error = self.gyroX / 2 - self.quad.getR()
				self.quad.setHpr(self.quad, 0, 0, error * 0.01)
				if self.isMoving:
					maxVelocity = 0.2
					sign = 1
					if self.quad.getR() < 0:
						sign = -1
					error = (sign * maxVelocity) - self.dX
					self.dX += error * 0.01
					self.camera.setPos(self.camera, self.dX, 0, 0)
					self.quad.setPos(self.camera, 0,self.quadDistance,-2)
			except: pass
			time.sleep(0.01)

	#This is prompted whenever the quad crosses the finish line. 

	def updateSaveTimer(self):
		if not self.timerRunning and self.timer != 0:
			text = 'Would you like to\nsave this time?\n(Y/N)'
			self.saveTimeText.setText(text)
		else:
			self.saveTimeText.setText('')

	#This is another stability algorithm tha tI wrote. Eseentially, it will
	#bring the copter to a smooth stop instead of it being jittery. However,
	#this can only work so well, as the quad is still 90% affected by the
	#physical orientation.

	def driftStabilize(self): 
		error = 0 - self.dX
		self.dX += error * 0.05
		self.camera.setPos(self.camera, self.dX, 0, 0)
		self.quad.setPos(self.camera, 0,self.quadDistance,-2)

	#controls the yaw direction of the quad. 

	def spinQuad(self, server):
		while True:
			try:
				if not self.noYawInput:
					sign = 1
					if self.yaw < 0:
						sign = -1
					self.dTheta = ((self.yaw / 100)) * self.cameraSpeed * 4
					self.camera.setHpr(self.camera, self.dTheta, 0,0)
					absRotationSpeed = abs(self.dTheta)
					deltaX = sign * (cos(radians(90 - absRotationSpeed)) * 
						self.quadDistance) * cos(radians(absRotationSpeed))
					deltaY = (cos(radians(90 - absRotationSpeed)) * 
						self.quadDistance) * sin(radians(absRotationSpeed))
					self.camera.setPos(self.camera, deltaX, deltaY, 0)
					self.quad.setPos(self.camera, 0,self.quadDistance, -2)
					self.quad.setHpr(self.camera, 0,self.quad.getP(),
						self.quad.getR())
			except: pass			
			time.sleep(0.01)

	#yaw refers to the rotation about its z axis. This will smoothen out
	#the quad's z axis rotation

	def yawSelfLevel(self):
		self.noYawInput = True
		error = 0 - self.dTheta
		self.dTheta += error * 0.05
		self.camera.setHpr(self.camera, self.dTheta, 0, 0)
		self.quad.setHpr(self.camera, 0, self.quad.getP(), self.quad.getR())
		self.quad.setPos(self.camera, 0, self.quadDistance, -2)

	#generic evaluateHits function. Will add more onto it later.

	def evaluateHits(self, server):
		while True:
			try:
				x = self.quad.getX()
				y = self.quad.getY()
				if (x > 18 and x < 38) and (y > 9 and y < 14):
					self.handleTimer()
				# self.helpText.setText(str(self.thr))
			except: pass
			time.sleep(0.1)

	#an issue that I ran into was having the timer run on and off when
	#the quad is hovering over the finish line, since it takes time
	#to actually physically cross the finish line. Therefore, I made a function
	#that makes sure the time between each time the quad hits the finish
	#line is greater than 1 second.

	def handleTimer(self):
		timeElapsed = self.calculateTime(self.getTime(), 
			self.timerLastModified)
		self.timerLastModified = self.getTime()
		if int(timeElapsed[0]) >= 1 or int(timeElapsed[1]) >= 1:
			self.startStopTimer()

	#this time method is run continuously. However, it will only actually do 
	#something if the self.timerRunning variable is true. It will update
	#the self.timerText text to the running time

	def runTimer(self, server):
		while True:
			if self.timerRunning:
				self.timer = self.calculateTime(self.getTime(),self.timerBegin)
				self.timerText.setText("Time: " + self.timer)
			time.sleep(0.1)

	#calculates the time elapsed given a current time and the start time.
	#return a string in the format MM:SS, unless one of those values = 0,
	#then it will ignore that part.

	def calculateTime(self, currentTime, startTime):
		(currentTime, startTime)=(currentTime.split(':'),startTime.split(':'))
		resultTimer = []
		for timerIndex in range(len(startTime)):
			diff=float(currentTime[timerIndex])-float(startTime[timerIndex])
			if diff < 0:
				diff += 60
				resultTimer[timerIndex -1 ] -= 1
			resultTimer.append(diff)
		time = ""
		(minutes,seconds)=(resultTimer[1],resultTimer[2])
		if minutes != 0:
			time += str(minutes)[0] + ":"
		if seconds != 0:
			seconds = str(seconds)[:4] + ":"
			if seconds.index('.') == 1: seconds = "0" + seconds
			time += seconds
		return time[:-1]

	#this is a thread that is constantly run to update the server variables
	#I ended up not using a bunch of these variables, because I ran into 
	#a lot of lag whenever I tried to constantly update textFields to read
	#whatever the server sends.

	def handleServerMsg(self, server):
		while True:
			msg = server.recv(1000).decode('UTF-8')
			try:
				msg = eval(msg)
				self.distance = msg["distance"]
				self.gyroX = msg["gyroX"]
				self.gyroY = msg["gyroY"]
				self.yaw = msg["yaw"] // 100
				self.ele = msg["ele"]
				self.rud = msg["rud"]
				self.thr = msg["thr"]
				# print(self.thr)
				self.ail = msg["ail"]
				# print(self.thr)
			except:
				pass

 
app = MyApp(server)
app.run()
