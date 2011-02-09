import sys
import time
import Queue
import serial

class DaqConnection(object):

    def __init__(self, inqueue, outqueue):

        try:
            self.port = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,parity='N',stopbits=1,timeout=0.5,xonxoff=True)
        except serial.SerialException, e:
            print e.message
            sys.exit(1)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.running = 1

    def read(self):
        min_sleeptime = 0.01 # seconds
        max_sleeptime = 0.2 # seconds
        sleeptime = min_sleeptime #seconds
        while self.running:
#            data = self.port.read(1)
#            n = self.port.inWaiting()
#            if n > 0:
#                data += self.port.read(n)
#            for line in data.split('\n'):
#                self.outqueue.put(line)
            if self.port.inWaiting():
                while self.port.inWaiting():
                    self.outqueue.put(self.port.readline().strip())
                sleeptime = max(sleeptime/2, min_sleeptime)
            else:
                sleeptime = min(1.5 * sleeptime, max_sleeptime)
            time.sleep(sleeptime)

    def write(self):
        while self.running:
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    pass
            time.sleep(0.1)

# vim: ai ts=4 sts=4 et sw=4