import time

class PIDController():
	def __init__(self, KP, KI, KD):
		self.KP = KP
		self.KI = KI
		self.KD = KD
		self.integral = 0
		self.prev_error = 0
		self.output = 0
		self.first = True

	def soft_reset(self):
		self.lasttime = time.clock()
		self.integral = 0
		self.output = 0
		self.prev_error = 0
		self.first = True

	def time_reset(self):
                self.lasttime = time.clock()

	def update(self, measured, setpoint):
		error = setpoint - measured
		
		now = time.clock()
		dt = now - self.lasttime
		self.lasttime = now

		self.integral += error*dt
		derivative = (error - self.prev_error)/dt
		output = self.KP*error + self.KI*self.integral + self.KD*derivative
		self.prev_error = error
		if self.first:
                        self.first = False
                        return 0
                #print "PID: " + str(self.KP*error) + "  " + str(self.KI*self.integral) + "  " + str(self.KD*derivative)
		return output
