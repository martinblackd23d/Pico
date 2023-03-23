import machine
import array
import time
import rp2
import math

#import pico_rdp
#import pico_4wd

#Debug Led on board
class DebugLed():
	timer = None
	#state = 0 #light state: 0 = off, 1 = on
	pin = None

	def __init__(self, pin = 25):
		self.pin = machine.Pin(pin, machine.Pin.OUT)

	def blink(self, t):
		#print(t)
		if t:
			self.pin.high()
		else:
			self.pin.low()

#RGB ligth strips
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
	T1 = 2
	T2 = 5
	T3 = 3
	label('bitloop')
	out(x, 1).side(0)[T3 - 1]
	jmp(not_x, 'do_zero').side(1)[T1 - 1]
	jmp('bitloop').side(1)[T2 - 1]
	label('do_zero')
	nop().side(0)[T2 - 1]

class Lights():
	timer = None
	colors = {
			1: 0xFFFFFF, #OK
			-1: 0xFF000000, #ERROR
			0: 0x000000, #light OFF
	}
	#state = 0 #light state: 0 = off, 1 = on
	status = 0 #machine status: 0 = OK, 1 = ERROR
	pin = None
	sm = None
	led_nums = 0
	buf = None

	def __init__(self, pin = 19, num = 24):
		self.pin = machine.Pin(pin, machine.Pin.OUT)
		self.led_nums = num
		self.sm = rp2.StateMachine(0, ws2812, freq=8000000, sideset_base=self.pin)
		self.sm.active(1)
		self.buf = array.array('I', [0 for _ in range(self.led_nums)])

	def write(self, is_on):
		for i in range(self.led_nums):
			if is_on:
				self.buf[i] = self.colors[self.status]
			else:
				self.buf[i] = self.colors[0]
		self.sm.put(self.buf, 8)
			
	def blink(self, t):
		self.write(t)

#blink control for debug led and RGB lights
class LightTimer():
	timer = None
	dbg = None
	rgb = None
	state = 0
	def __init__(self, dbg, rgb):
		self.dbg = dbg
		self.rgb = rgb
		self.timer = machine.Timer()
		self.timer.init(mode = machine.Timer.PERIODIC, period = 500, callback = self.blink)

	def blink(self, t):
		self.state = (self.state + 1) % 2
		self.dbg.blink(self.state == 1)
		self.rgb.blink(self.state == 1)


class Motor():
	pin_1 = None
	pin_2 = None
	#dir = 1
#	curr = 0
	power = 0
	max = 100
	min = 20

	#def __init__(self, pin_1, pin_2, dir = 1):
	def __init__(self, pin_1, pin_2):
		self.pin_1 = machine.PWM(machine.Pin(pin_1, machine.Pin.OUT))
		self.pin_2 = machine.PWM(machine.Pin(pin_2, machine.Pin.OUT))
		self.pin_1.freq(20000)
		self.pin_2.freq(20000)
		#self.dir = dir

	def cycle(self):
		#if self.curr < self.power:
		#	self.curr += 1
		#elif self.curr > self.power:
		#	self.curr -= 1

		value = 0xffff - 0xffff / 100 * (self.min + abs(self.power) / 100 * (self.max - self.min))
		print(f'{self.power}\t{int(value)}')
		if self.power > 0:
			self.pin_1.duty_u16(0x0000)
			self.pin_2.duty_u16(0xffff)
		if self.power < 0:
			self.pin_1.duty_u16(0xffff)
			self.pin_2.duty_u16(0x0000)
		else:
			self.pin_1.duty_u16(0x0000)
			self.pin_2.duty_u16(0xffff)

class Drive():
	lf = None
	rf = None
	lb = None
	rb = None
	speed = 0
	status = 0	#-1: hard stop 0: stop, 1: move, 2: long turn, 3: in-place turn
	turn = 10	#difference between left and right side power
				#when long turning

	def __init__(self):
		#lf = Motor(16, 17, 1)
		#rb = Motor(14, 15, -1)
		#lb = Motor(12, 13, 1)
		#rf = Motor(10, 11, -1)
		self.lf = Motor(16, 17)
		self.rb = Motor(15, 14)
		self.lb = Motor(12, 13)
		self.rf = Motor(11, 10)
		for i in [self.lf, self.rf, self.lb, self.rb]:
			#print(i)
			i.power = 0
			i.cycle()

	def hardstop(self):
		for i in [self.lf, self.rf, self.lb, self.rb]:
			i.power = 0
			i.cycle()

	def move(self):
		#print(f'{self.status}\t{self.speed}')
		for i in [self.lf, self.rf, self.lb, self.rb]:
			if i.power < self.speed:
				i.power += 1
			elif i.power > self.speed:
				i.power -= 1
			i.cycle()

	def stop(self):
		#print('stop')
		for i in [self.lf, self.rf, self.lb, self.rb]:
			if i.power > 0:
				i.power -= 1
			elif i.power < 0:
				i.power += 1
			i.cycle()

	def lturn(self):
		pass

	def iturn(self):
		pass

	def update(self):
		[self.stop, self.move, self.lturn, self.iturn, self.hardstop][self.status]()




class grayscale():
	gs0 = None
	gs1 = None
	gs2 = None

	def __init__(self, pin0 = 26, pin1 = 27, pin2 = 28):
		self.gs0 = machine.ADC(machine.Pin(26))
		self.gs1 = machine.ADC(machine.Pin(27))
		self.gs2 = machine.ADC(machine.Pin(28))

	def display(self):
		print(f'{self.gs0.read_u16()}\t{self.gs1.read_u16()}\t{self.gs2.read_u16()}')

#main function
def main(main_count, lights, drive, gs):
	#lights.status(0)
	drive.lf.power = 100
	drive.lf.cycle()
	return

	if int(main_count / 250) % 2 == 0:
		drive.speed = 100
		drive.status = 1
	else:
		drive.status = 0

	drive.update()
	#gs.display()
	return

if __name__ == '__main__':
	main_count = 0					#number of times the main loop executed
	start_time = time.time()		#time execution started
	main_dur = 20					#length of a single loop in ms
	delta = 0						#time remaining from previous loop
	
	lights = Lights()
	debugled = DebugLed()

	drive = Drive()

	t = LightTimer(debugled, lights)

	lights.status = 1

	gs = grayscale()

	while True:
		loop_start = time.time()
		main(main_count, lights, drive, gs)
		main_count += 1
		loop_end = time.time()
		delta = loop_end - loop_start
		if delta < 20:
			time.sleep_ms(20 - delta)