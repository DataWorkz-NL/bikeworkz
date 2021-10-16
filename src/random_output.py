import os
import random

f = open("joep.log",'w')
try:
	while True:
		output = str(random.choice([0, 1, 2,3])) + str(random.choice([0, 1]))

		# print(output)
		f.seek(0)
		f.write(output)
finally:
	f.close()