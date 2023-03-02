import machine
import array
import time
import rp2
import math

#import pico_rdp
#import pico_4wd

class DebugLed():
	timer = None
	state = 0
	pin = None

	def __init__(self):
		self.pin = machine.Pin(25, machine.Pin.OUT)
		self.timer = machine.Timer()
		self.timer.init(mode = machine.Timer.PERIODIC, period = 500, callback = self.blink)
		return

	def blink(self, t):
		print(t)
		self.state = (self.state + 1) % 2
		if self.state == 0:
			self.pin.low()
		elif self.state == 1:
			self.pin.high()
		return

class Lights():
	timer = None
	colors = {
			'white': None
	}
	color = ''
	#status = 0

	def __init__(self):
		return


	def blink(self, color):
		pass

	def status(self, status):
		if status == 0:
			self.blink('white')
		else:
			self.blink('red')

def main(main_count, lights):
	#lights.status(0)
	time.sleep(1)
	return

if __name__ == '__main__':
	main_count = 0					#number of times the main loop executed
	start_time = time.time()		#time execution started
	main_dur = 20					#length of a single loop in ms
	delta = 0						#time remaining from previous loop
	
	#lights = Lights()
	debugled = DebugLed()

	while True:
		loop_start = time.time()
		main(main_count, None)
		main_count += 1
		loop_end = time.time()
		delta = loop_end - loop_start
		if delta < 20:
			time.sleep_ms(20 - delta)