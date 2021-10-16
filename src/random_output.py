import os
import random

f = open("willem.log",'w')
try:
	while True:
		output = str(random.choice([0, 1, 2]))

		# print(output)
		f.seek(0)
		f.write(output)
finally:
	f.close()