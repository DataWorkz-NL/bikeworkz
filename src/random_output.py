import os
import random

options = [0, 1, 2]

while True:
	output = str(random.choice([0, 1, 2]))

	# print(output)
	f = open("willem.log",'w')
	f.write(output)
	f.close()