import serial
import time
# print(lines[0])

def one():
	ser.write(b'w')
	time.sleep(0.5)
	ser.write(b'r')
	time.sleep(0.5)
	ser.write(b't')
	return "green"
 
def two():
	ser.writelines(b'w')
	ser.writelines(b'e')
	ser.writelines(b'y')
	return "yellow"
 
def three():
	ser.writelines(b'q')
	ser.writelines(b'r')
	ser.writelines(b'y')
	return "red"

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


ser = serial.Serial('/dev/cu.usbserial-145330', 9800)


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
		time.sleep(0.5) 
		f.seek(0)
finally:
	f.close()
	ser.close()
