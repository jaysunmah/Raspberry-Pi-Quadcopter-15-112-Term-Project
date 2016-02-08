import time

prevError = 0
integral = 0
Kp = 0.2
Ki = 0.00001
Kd = 0.00001
desiredVal = 2
actualVal = 0
deltaT = 0.1

#the whole purpose of this code is for stabilization. How much input
#is needed at a given moment such that the change in stabilization inputs
#is smooth.

while True:
	error = desiredVal - actualVal
	integral = integral + (error * deltaT)
	derivative = (error - prevError) / deltaT
	actualVal += Kp * error + Ki * integral + Kd * derivative
	print(actualVal)
	prevError = error
	time.sleep(deltaT)


#I didn't derive this stabilization algorithm, but I forget if I copied
#this code exactly or if I paraphrased it. I'm not currently using this code, 
#but I plan on implementing it soon for more flight simulation stability

def getChange(desiredVal, actualVal, prevError = 0, Kp = 0.2, Ki = 0.00001, 
	Kd = 0.00001, deltaT = 0.1):
	error = desiredVal - actualVal
	integral = integral + (error * deltaT)
	derivative = (error - prevError) / deltaT
	return Kp * error + Ki * integral + Kd * derivative



