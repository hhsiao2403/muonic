import sys

for line in open(sys.argv[1]).readlines():
    fields = line.split(' ')
    for field in fields:
        try:
            print float(field)
        except ValueError:
            pass

# vim: ai ts=4 sts=4 et sw=4
