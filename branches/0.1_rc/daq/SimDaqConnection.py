#! /usr/bin/env python

"""
Provides a simple DAQ card simulation, so that software can testet with it
"""

import time
import Queue
import numpy as n
from random import choice
	
class SimDaq():

    def __init__(self, logger):
        
        self.logger = logger
        self.logger.debug("called")
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
            return hexstring.zfill(8)
        

        # draw rates from a poisson distribution,
        scalars_ch0 = int(choice(n.random.poisson(12,100)))
        self.logger.debug("scalars_ch0 %f" %scalars_ch0)
        scalars_ch1 = int(choice(n.random.poisson(10,100)))
        scalars_ch2 = int(choice(n.random.poisson(8,100)))
        scalars_ch3 = int(choice(n.random.poisson(11,100)))
        scalars_trigger = scalars_ch0 + scalars_ch1 + scalars_ch2 + scalars_ch3

        self.__scalars_ch0__ += scalars_ch0
        self.__scalars_ch1__ += scalars_ch1
        self.__scalars_ch2__ += scalars_ch2
        self.__scalars_ch3__ += scalars_ch3
        self.__scalars_trigger__ += scalars_trigger


        self.__scalars_to_return__ = 'DS S0=' + format_to_8digits(hex(self.__scalars_ch0__)[2:]) + ' S1=' + format_to_8digits(hex(self.__scalars_ch1__)[2:]) + ' S2=' + format_to_8digits(hex(self.__scalars_ch2__)[2:]) + ' S3=' + format_to_8digits(hex(self.__scalars_ch3__)[2:]) + ' S4=' + format_to_8digits(hex(self.__scalars_trigger__)[2:])
        self.logger.debug("Scalars to return %s" %self.__scalars_to_return__)

    def __reload__(self):
        self.logger.debug("File reloaded")
        self.__daq__ = open(self.__simdaq_file__)

    def readline(self):

        self.logger.debug("return info %s" %self.__return_info__)
        if self.__return_info__:
            self.logger.debug("info field: %s" %self.__info__) 
            self.__return_info__ = False
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
        
        time.sleep(seconds)
        self.__physics__()

    def push_info(self):
        return self.__info__


    def write(self,command):
        if "DS" in command:
            self.__info__ = self.__scalars_to_return__
            self.__return_info__ = True
            self.logger.debug("got DS command, setting return info to %s" %self.__return_info__) 
            return self.__info__
        else:
            self.logger.debug("called")
            pass

    def inWaiting(self):
        if self.__inWaiting__:
            self.__wait__(0.3)
            return True

        else:
            #self.__inWaiting__ = True
            return False
        
       

class SimDaqConnection(object):

    def __init__(self, inqueue, outqueue, logger):

        self.logger = logger
        self.port = SimDaq(self.logger)
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
            
            self.logger.info("inqueue size is %d" %self.inqueue.qsize())
            while self.inqueue.qsize():
                try:
                    self.port.write(str(self.inqueue.get(0))+"\r")
                    #self.inqueue.task_done()
                except Queue.Empty:
                    self.logger.debug("Queue empty!")
                    pass
            
            if self.port.inWaiting():
                while self.port.inWaiting():
                    self.outqueue.put(self.port.readline().strip())
                    if self.port.__return_info__:
                        self.logger.debug("returning info")
                        self.outqueue.put(self.port.push_info())
                        self.port.__inWaiting__ = False
                    #self.outqueue.task_done()
                sleeptime = max(sleeptime/2, min_sleeptime)
                self.port.__inWaiting__ = True
            else:
                sleeptime = min(1.5 * sleeptime, max_sleeptime)

            time.sleep(sleeptime)


