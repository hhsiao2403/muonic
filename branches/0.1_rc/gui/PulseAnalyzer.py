#! /usr/env/bin python


BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1 # 1 PPS interrupt pending
BIT1 = 1 << 1 # Trigger interrupt pending
BIT2 = 1 << 2 # GPS data possible corrupted
BIT3 = 1 << 3 # Current or last 1PPS rate not within range

cpld_freq = 25.0e6 # TODO: We have to make sure that this is the right frequency
MINI_TICK = 1.0/(cpld_freq * 32)

#assuming the cpld clock runs with approx 41MHz
cpld_tick = 24  #nsec 
tmc_tick = 0.75 #nsec

# get the pulses out of a daq line
# we have to be as fast as possible!

from get_time import get_time

class PulseExtractor:

    def __init__(self,pulsefile=''):
        """
        if a pulsefile is given, all the extracte pulses
        will be written into it
        """

        
        self.chan0re = []
        self.chan0fe = []
        self.chan1re = []
        self.chan1fe = []
        self.chan2re = []
        self.chan2fe = []
        self.chan3re = []
        self.chan3fe = []
        self.lastchan0re = []
        self.lastchan0fe = []
        self.lastchan1re = []
        self.lastchan1fe = []
        self.lastchan2re = []
        self.lastchan2fe = []
        self.lastchan3re = []
        self.lastchan3fe = []
        
        self.pulsedict = dict()

        self.trigger = 0
        self.pulsefile = pulsefile
        if pulsefile:
            self.pulsefile = open(pulsefile,'w')           
        self.ini = True

    def calculate_edges(self,line):
        if (int(line[1],16) & BIT5):
            self.chan0re.append((self.linetime - self.trigger) + (int(line[1],16) & BIT0_4)*tmc_tick) 
        if (int(line[2],16) & BIT5):
            self.chan0fe.append((self.linetime - self.trigger) + (int(line[2],16) & BIT0_4)*tmc_tick)
        if (int(line[3],16) & BIT5):
            self.chan1re.append((self.linetime - self.trigger) + (int(line[3],16) & BIT0_4)*tmc_tick)
        if (int(line[4],16) & BIT5):
            self.chan1fe.append((self.linetime - self.trigger) + (int(line[4],16) & BIT0_4)*tmc_tick)
        if (int(line[5],16) & BIT5):
            self.chan2re.append((self.linetime - self.trigger) + (int(line[5],16) & BIT0_4)*tmc_tick)
        if (int(line[6],16) & BIT5):
            self.chan2fe.append((self.linetime - self.trigger) + (int(line[6],16) & BIT0_4)*tmc_tick)
        if (int(line[7],16) & BIT5):
            self.chan3re.append((self.linetime - self.trigger) + (int(line[7],16) & BIT0_4)*tmc_tick)
        if (int(line[8],16) & BIT5):
            self.chan3fe.append((self.linetime - self.trigger) + (int(line[8],16) & BIT0_4)*tmc_tick)

    def order_and_cleanpulses(self):
        """
        Remove pulses which have a 
        leading edge later in time than a 
        falling edge and do a bit of sorting
        """


        self.chan0 = zip(self.lastchan0re,self.lastchan0fe)
        for i in self.chan0:
            if not i[0] < i[1]:
                self.chan0.remove(i)
           
        self.chan1 = zip(self.lastchan1re,self.lastchan1fe)
        for i in self.chan1:
            if not i[0] < i[1]:
                self.chan1.remove(i)

        self.chan2 = zip(self.lastchan2re,self.lastchan2fe)
        for i in self.chan2:
            if not i[0] < i[1]:
                self.chan2.remove(i)

        self.chan3 = zip(self.lastchan3re,self.lastchan3fe)
        for i in self.chan3:
            if not i[0] < i[1]:
                self.chan3.remove(i)

    def extract(self,line):
        """Search for triggers in a set of lines"""


        line = line.split()

        if self.ini:
            self.lastonepps = int(line[9],16)
            self.ini = False
            print 'ini'
            return None
        #self.linetime = int(line[0],16)*cpld_tick
        self.linetime = get_time(line,self.lastonepps)
        self.lastonepps = int(line[9],16)
        self.triggerflag = int(line[1],16)     


        if (self.triggerflag < 80): 
            # we do have a previous trigger and are now adding more pulses to the event

            if self.trigger:
                self.calculate_edges(line)
  
        if self.triggerflag >= 80:
            # a new trigger!o we have to evaluate the last one and get the new pulses
            self.lasttriggertime = self.trigger
            self.lastchan0re = self.chan0re
            self.lastchan0fe = self.chan0fe
            self.lastchan1re = self.chan1re
            self.lastchan1fe = self.chan1fe
            self.lastchan2re = self.chan2re
            self.lastchan2fe = self.chan2fe
            self.lastchan3re = self.chan3re
            self.lastchan3fe = self.chan3fe

            #self.trigger = int(line[0],16)*cpld_tick
            self.trigger = get_time(line,self.lastonepps)
            self.linetime = self.trigger

            self.chan0re = []  
            self.chan0fe = []
            self.chan1re = []
            self.chan1fe = []
            self.chan2re = []
            self.chan2fe = []
            self.chan3re = []
            self.chan3fe = []
           

            
            self.calculate_edges(line)
            self.order_and_cleanpulses()

            extracted_pulses = (self.lasttriggertime,self.chan0,self.chan1,self.chan2,self.chan3) 
            if self.pulsefile:
                self.pulsefile.write(extracted_pulses.__repr__() + '\n')


            return extracted_pulses
 

    def close_file(self):
        self.pulsefile.close()          



# trigger on a set of extracted pulses and look for decayed muons
# this trigger builds from DAQ triggers....


class DecayTrigger:
    """
    This trigger is designed to decide wether to adjacent triggers
    occur within 20microseconds
    """   


    def __init__(self,triggerpulses,chan3softveto):
        self.triggerwindow = 2000 # 20microseconds
        self.lasttriggerpulses = triggerpulses
        self.chan3softveto = chan3softveto

    def trigger(self,thistriggerpulses):
     
           # decay time based only on cpld clock!
           if self.chan3softveto:
               if (not self.lasttriggerpulses[4]) & (not thistriggerpulses[4]):
	           # we simply subtract two trigger times!
                   decaytime0 = thistriggerpulses[0] - self.lasttriggerpulses[0]
	
                   #print decaytime
                   if decaytime < self.triggerwindow:
             	       print 'We registered a decayed muon'
                       self.lasttriggerpulses = thistriggerpulses
                       if not decaytime < 0:
                            self.lasttriggerpulses = thistriggerpulses
                            return decaytime

                       else:
                           self.lasttriggerpulses = thistriggerpulses

               else:
                   self.lasttriggerpulses = thistriggerpulses


           else:
               decaytime = thistriggerpulses[0] - self.lasttriggerpulses[0]
               #print decaytime
               if decaytime < self.triggerwindow:
                   print 'We registered a decayed muon'
                   self.lasttriggerpulses = thistriggerpulses
                   if not decaytime < 0:
                       return decaytime
	

               else:
                   self.lasttriggerpulses = thistriggerpulses 

           ###############################################
           # what is below was tried to be more accurate,
           # but seems to complicated
           # anyone's ideas are very welcome
           ###############################################


           ## check if the triggertimes are within the triggerwindow

           ## we have also to ensure that the trigger is not caused by
           ## some coincident muon, so we demand that there is only
           ## one pulse in the second trigger


           ## the second condition checks if the lists are empty,
           ## remember also that the first item of some pulse tuple
           ## is always the cpld triggertime
           ## so '==1' ensures that we have only pulses in one channel
    

           ##chanpulsecount = [thistriggerpulses.index(pulse) for pulse in thistriggerpulses[:1] if pulse]
           ##secondtriggercondition = len(chanpulsecount) == 1 

           ##if (self.lasttriggerpulses[0] - thistriggerpulses[9] < 20000) and secondtriggercondition:
           ##    if thistriggerpulses[chanpulsecount[0]]: 
           ##        print 'We have a decaying Muon!'



    ##def lifetimecalculator(self,lastpulses,thispulses):
      
           ## if we have a trigger, we want to know exactly
           ## how far the two pulses are apart



           
 


if __name__ == '__main__':

    line = '6B00BC12 00 30 00 31 00 00 00 00 00000002 000000.000 000000 V 00 8 +0000'
    	
    data = open('../simdaq.txt')
    extractor = PulseExtractor()
    while True:
        try:
            print extractor.extract(data.readline())
            #print extractor.chan1fe
        except ValueError:
            print 'VE'



