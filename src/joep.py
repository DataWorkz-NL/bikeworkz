import serial
import time
# print(lines[0])

def one():
	ser.write(b'w')
	time.sleep(0.1)
	ser.write(b'r')
	time.sleep(0.1)
	ser.write(b't')
	time.sleep(0.1)
	print( "green")
 
def two():
	ser.write(b'w')
	time.sleep(0.1)
	ser.write(b'e')
	time.sleep(0.1)
	ser.write(b'y')
	time.sleep(0.1)
	print("yellow")
 
def three():
	ser.write(b'q')
	time.sleep(0.1)
	ser.write(b'r')
	time.sleep(0.1)
	ser.write(b'y')
	time.sleep(0.1)
	print( "red")

def numbers_to_function(argument):
	switcher = {
		'0': one,
		'1': two,
		'2': three
	}
	# Get the function from switcher dictionary
	func = switcher.get(argument, lambda: "Invalid function")
	# Execute the function
	func()


ser = serial.Serial('/dev/cu.usbserial-145330', 115200)
# sleep for device getting ready
time.sleep(0.1)
# ser.writelines(b'q')
# time.sleep(0.5)
# one()
# ser.close()



f = open("willem.log",'r')

lines = f.readlines()

try:
	while True:
		# lines = f.readlines()
		# print(lines)
		first_line = f.readline()
		numbers_to_function(first_line)
		# time.sleep(0.5) 
		f.seek(0)
finally:
	f.close()
	ser.close()
