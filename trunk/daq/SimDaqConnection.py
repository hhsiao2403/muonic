import sys
import time
import Queue

class SimDaq():

    def __init__(self):
        self.__pushed_lines__ = 0
        self.__lines_to_push__ = 10
        self.__simdaq_file__ = "simdaq.txt"
        self.__daq__ = open(self.__simdaq_file__)
        self.__inWaiting__ = True
        self.__return_info__ = False
        self.__info__ = ""

    def __reload__(self):
        print "FILE RELOADED"
        self.__daq__ = open(self.__simdaq_file__)

    def readline(self):

        if self.__return_info__:
            self.__return_info__ = False
            print self.__info__
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
        print "SIMULATION MODE!"
        self.__inWaiting__ = True


    def write(self,command):
        if "DS" in command:
            print "SIMDAQ: got DS command" 
            self.__info__ = "DS S0=00000064 S1=000000c8 S2=0000012c S3=00000190 S4=000003e8 S5=00000020"
            self.__return_info__ = True
        

    def inWaiting(self):
        if not self.__inWaiting__:
            self.__wait__(2)

        return self.__inWaiting__
        
       

class SimDaqConnection(object):

    def __init__(self, inqueue, outqueue):

        self.port = SimDaq()
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
