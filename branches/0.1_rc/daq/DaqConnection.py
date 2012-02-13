import sys
import time
import Queue
import serial

class DaqConnection(object):

    def __init__(self, inqueue, outqueue, logger):

        try:
            self.port = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,parity='N',stopbits=1,timeout=0.5,xonxoff=True)
        except serial.SerialException, e:
            print e.message
            sys.exit(1)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.running = 1
        self.logger = logger

    def get_port():
        connected = False
        while not connected:
            dev = subprocess.Popen(['which_tty_daq'], stdout=subprocess.PIPE).communicate([0])
            dev = "/dev/" + dev
            dev = dev.rstrip('\n')
            self.logger.info("Daq connected to %s",dev)
            try:
                port = serial.Serial(port=dev, baudrate=115200,
                                     bytesize=8,parity='N',stopbits=1,
                                     timeout=1,xonxoff=True)
                connected = True
            except serial.SerialException, e:
                logger.error(e)
                logger.error("Waiting 10 seconds")
                time.sleep(10)

        self.logger.info("Successfully connected to serial port")
        return port



    def read(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """
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
            try:
                if self.port.inWaiting():
                    while self.port.inWaiting():
                        self.outqueue.put(self.port.readline().strip())
                    sleeptime = max(sleeptime/2, min_sleeptime)
                else:
                    sleeptime = min(1.5 * sleeptime, max_sleeptime)
                time.sleep(sleeptime)

            except IOError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                # this has to be implemented in the future
                # for now, we assume that the card does not forget
                # its settings, only because the USB connection is
                # broken
                #self.setup_daq.setup(self.commandqueue)
            except OSError:
                self.logger.error("IOError")
                self.port.close()
                self.port = self.get_port()
                #self.setup_daq.setup(self.commandqueue)



    def write(self):
        while self.running:
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                except Queue.Empty:
                    pass
            time.sleep(0.1)

# vim: ai ts=4 sts=4 et sw=4
