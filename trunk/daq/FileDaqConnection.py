import sys
import time
import Queue
import numpy as n
import gc
from random import choice
	
class FileDaq():

    def __init__(self,infile, logger):
        
        self.logger = logger
        self.__pushed_lines__ = 0
        self.__lines_to_push__ = 10
        self.__daq__ = open(infile)
        self.__inWaiting__ = True 


    def readline(self):


        self.__pushed_lines__ += 1
        line = self.__daq__.readline()
        return line
            

    def __wait__(self,seconds):
        
        time.sleep(seconds)
        self.logger.debug("Read from file!")

    def write(self,command):
        pass

    def inWaiting(self):
        if self.__inWaiting__:
            self.__wait__(0.3)
            #self.__inWaiting__ = choice([True,False])
            return True

        else:
            #self.__inWaiting__ = True
            return False
        
       

class FileDaqConnection(object):

    def __init__(self, inqueue, outqueue,infile, logger):

        self.logger = logger
        self.port = FileDaq(infile,self.logger)
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
        self.logger.info('')
        while self.running:
            
            
            self.outqueue.put(self.port.readline().strip())
            sleeptime = max(sleeptime/2, min_sleeptime)
            time.sleep(sleeptime)

