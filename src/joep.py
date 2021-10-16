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
time.sleep(2)

def parse_code(code: str) -> str:
    if code[0] == '0':
        return b's'
    if code[0] == '1':
        return b'a'
    elif code[0] == '2':
        return b'w'
    elif code[0] == '3':
        return b'd'
    else:
        return b's'

f = open("joep.log",'r')

try:
    while True:
        code = f.readline()
        
        payload = parse_code(code)
        respsonse = ser.write(payload)
        time.sleep(0.1)
        f.seek(0)
finally:
    f.close()
    ser.close()
