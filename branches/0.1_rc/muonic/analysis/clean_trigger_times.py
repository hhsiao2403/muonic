


import sys

for line in open(sys.argv[1]).readlines():

     if float(line) > 10:
        continue

     else:
        print float(line) 
