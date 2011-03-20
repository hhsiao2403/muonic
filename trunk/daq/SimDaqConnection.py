import sys
import time
import Queue
import numpy as n

class SimDaq():

    def __init__(self, debug):
        
        self.debug = debug
        self.__pushed_lines__ = 0
        self.__lines_to_push__ = 10
        self.__simdaq_file__ = "simdaq.txt"
        self.__daq__ = open(self.__simdaq_file__)
        self.__inWaiting__ = True
        self.__return_info__ = False
        self.__info__ = ""
        self.__scalars_ch0__ = 0
        self.__scalars_ch1__ = 0
        self.__scalars_ch2__ = 0
        self.__scalars_ch3__ = 0
        self.__scalars_trigger__ = 0
        self.__scalars_to_return__ = ''

    def __physics__(self):
        """
        This routine will increase the scalars variables using predefined rates
        """
	
        def format_to_8digits(hexstring):
            if len(hexstring) < 8:
                zeros_to_add = 8-len(hexstring)
                for zero in xrange(zeros_to_add):
                    hexstring = '0' + hexstring
                return hexstring
              
            if len(hexstring) > 8:
                return hexstring[-8:]
            else:
                pass

              
        scalars_ch0 = int(n.random.normal(10,4.0,100)[0])
        scalars_ch1 = int(n.random.normal(15,2.0,100)[0])
        scalars_ch2 = int(n.random.normal(9,3.0,100)[0])
        scalars_ch3 = int(n.random.normal(22,5.0,100)[0])
        scalars_trigger = scalars_ch0 + scalars_ch1 + scalars_ch2 + scalars_ch3

        self.__scalars_ch0__ += scalars_ch0
        self.__scalars_ch1__ += scalars_ch1
        self.__scalars_ch2__ += scalars_ch2
        self.__scalars_ch3__ += scalars_ch3
        self.__scalars_trigger__ += scalars_trigger


        self.__scalars_to_return__ = 'DS S0=' + format_to_8digits(hex(self.__scalars_ch0__)[2:]) + ' S1=' + format_to_8digits(hex(self.__scalars_ch1__)[2:]) + ' S2=' + format_to_8digits(hex(self.__scalars_ch2__)[2:]) + ' S3=' + format_to_8digits(hex(self.__scalars_ch3__)[2:]) + ' S4=' + format_to_8digits(hex(self.__scalars_trigger__)[2:])
        #if self.debug: print self.__scalars_to_return__



    def __reload__(self):
        if self.debug: print "FILE RELOADED"
        self.__daq__ = open(self.__simdaq_file__)

    def readline(self):

        if self.__return_info__:
            self.__return_info__ = False
            if self.debug: print self.__info__
            return self.__info__

        self.__pushed_lines__ += 1
        if self.__pushed_lines__ < self.__lines_to_push__:
            line = self.__daq__.readline()
            if not line:
                self.__reload__()
                line = self.__daq__.readline()

            return line
        else:
            self.__pushed_lines__ = 0
            self.__inWaiting__ = False
            return self.__daq__.readline()
            

    def __wait__(self,seconds):
        
        self.__inWaiting__ = False
        time.sleep(seconds)
        self.__physics__()
        if self.debug: print "SIMULATION MODE!"
        self.__inWaiting__ = True


    def write(self,command):
        if "DS" in command:
            if self.debug: print "SIMDAQ: got DS command" 
            #self.__info__ = "DS S0=00000064 S1=000000c8 S2=0000012c S3=00000190 S4=000003e8 S5=00000020"
            self.__info__ = self.__scalars_to_return__
	    self.__return_info__ = True
        

    def inWaiting(self):
        if not self.__inWaiting__:
            self.__wait__(2)

        return self.__inWaiting__
        
       

class SimDaqConnection(object):

    def __init__(self, inqueue, outqueue, debug):

        self.debug = debug
        self.port = SimDaq(self.debug)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.running = 1

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
