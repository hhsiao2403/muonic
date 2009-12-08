import sys

for line in open(sys.argv[1]).readlines():
    fields = line.split(' ')
    for field in fields:
        try:
            print float(field)
        except ValueError:
            pass
