#! /usr/env/bin python

# for the pulses 
# 8 bits give a hex number
# but only the first 5 bits are used for the pulses time,
# the fifth bit flags if the pulse is considered valid
# the seventh bit should be the triggerflag...
BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1 # 1 PPS interrupt pending
BIT1 = 1 << 1 # Trigger interrupt pending
BIT2 = 1 << 2 # GPS data possible corrupted
BIT3 = 1 << 3 # Current or last 1PPS rate not within range

# ticksize of tmc internal clock
# documentation says 0.75, measurement says 1.25
# TODO: find out if tmc is coupled to cpld!
tmc_tick = 1.25 #nsec
MAX_TRIGGERWINDOW = 60.0 #nsec


#import numpy

class PulseExtractor:
    """
    get the pulses out of a daq line
    we have to be as fast as possible!
    """

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
        
        self.lasttriggertime = 0

        # store the actual value of
        # the trigger counter
        # to correct trigger counter rollover
        self.lasttriggercount = 0

        self.pulsefile = pulsefile
        if pulsefile:
            self.pulsefile = open(pulsefile,'w')           

        # ini will be False if we have seen the first 
        # trigger
        self.ini = True
        self.lastonepps = 0.
        self.gps_evttime = 0.
	self.linetime    = 0.

        # variables for DAQ frequency calculation
        self.lastfrequencypolltime = 0
        self.lastfrequencypolltriggers = 0
        # TODO find a generic way to account
        # for the fact that the default
        # cna be either 25 or 41 MHz
        self.calculatedfrequency = 25.0e6
        self.defaultfrequency    = 25.0e6
        self.pollcount           = 0
        self.lastoneppspoll      = 0
        self.passedonepps        = 0 
        #self.lasttime            = 0
	self.lastlinetime        = 0
        self.prevlast_onepps     = 0
        self.lastlinegpstime     = 0
        #self.rel_linetime        = 0 
        #self.lastrellinetime    = 0
        self.debug_freq = open('frequency.txt','w')
        self.debug_freq.write('#  sec (le (nsec), fe(nsec)) chan0 chan1 chan2 chan3 \n')
	self.trigger_count       = 0

    def calculate_edges(self,line,counter_diff=0):

        re0 = int(line[1],16)
        fe0 = int(line[2],16)
        re1 = int(line[3],16)
        fe1 = int(line[4],16)
        re2 = int(line[5],16)
        fe2 = int(line[6],16)
        re3 = int(line[7],16)
        fe3 = int(line[8],16)
        
        if (re0 & BIT5):    
            self.chan0re.append(counter_diff + (re0 & BIT0_4)*tmc_tick)  
        if (fe0 & BIT5):
            self.chan0fe.append(counter_diff + (fe0 & BIT0_4)*tmc_tick)
        if (re1 & BIT5):
            self.chan1re.append(counter_diff + (re1 & BIT0_4)*tmc_tick)
	    #print 're1', counter_diff,(re1 & BIT0_4)*tmc_tick
        if (fe1 & BIT5):
            self.chan1fe.append(counter_diff +(fe1 & BIT0_4)*tmc_tick)
	    #print 'fe1', counter_diff,(fe1 & BIT0_4)*tmc_tick
        if (re2 & BIT5):
            self.chan2re.append(counter_diff +(re2 & BIT0_4)*tmc_tick)
        if (fe2 & BIT5):
            self.chan2fe.append(counter_diff +(fe2 & BIT0_4)*tmc_tick)
        if (re3 & BIT5):
            self.chan3re.append(counter_diff +(re3 & BIT0_4)*tmc_tick)
        if (fe3 & BIT5):
            self.chan3fe.append(counter_diff +(fe3 & BIT0_4)*tmc_tick)

    def order_and_cleanpulses(self):
        """
        Remove pulses which have a 
        leading edge later in time than a 
        falling edge and do a bit of sorting
        Remove also single leading or falling edges
        NEW: We add virtual falling edges!
        """

        self.chan0 = zip(self.lastchan0re,self.lastchan0fe)
        for index,i in enumerate(self.chan0):
            if not i[0] < i[1]:
                #self.chan0.remove(i)
                self.chan0[index] = (i[0],MAX_TRIGGERWINDOW)

        self.chan1 = zip(self.lastchan1re,self.lastchan1fe)
        for index,i in enumerate(self.chan1):
            if not i[0] < i[1]:
                #self.chan1.remove(i)
		#print i[0],i[1],'removing'
                # adding virtual falling edge
                self.chan1[index] = (i[0],MAX_TRIGGERWINDOW)
		#print self.chan1[index],'fixed'
        self.chan2 = zip(self.lastchan2re,self.lastchan2fe)
        for index,i in enumerate(self.chan2):
            if not i[0] < i[1]:
                #self.chan2.remove(i)
                self.chan2[index] = (i[0],MAX_TRIGGERWINDOW)

        self.chan3 = zip(self.lastchan3re,self.lastchan3fe)
        for index,i in enumerate(self.chan3):
            if not i[0] < i[1]:
                #self.chan3.remove(i)
                self.chan3[index] = (i[0],MAX_TRIGGERWINDOW)

    def get_gps_time(self,time, correction):
        '''
        Convert hhmmss,xxx string int seconds since day start
        '''

        # since evt times can be rather large
        # we want to return longs here
        tfields = time.split(".")
        t = tfields[0]
        secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])
        evt_time = float(secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0)
        self.gps_evttime = evt_time
        # evt time is in milliseconds!
        return evt_time
   
    def get_rel_time(self,trigger_count,thisonepps):

        line_time = (trigger_count - thisonepps)/self.calculatedfrequency
        return line_time
 
    def get_time(self,trigger_count,prevlast=False):
        """
        Get the actual absolute time 
        of the event in seconds
        """
        #print '-----------'
        #print trigger_count,'triggercount'
        #print self.gps_evttime, 'gps'
        #print self.lastonepps, 'lastonepps'
        debug_diff = trigger_count -self.lastonepps
        #print debug_diff,'diff'
	#print self.calculatedfrequency,'freq'
        #print debug_diff/self.calculatedfrequency,'diff/freq'
        
        if prevlast:
            line_time = self.gps_evttime + float((trigger_count - self.prevlast_onepps)/self.calculatedfrequency)
        else:
            line_time = self.gps_evttime + float((trigger_count - self.lastonepps)/self.calculatedfrequency)
        # line time is in microseconds
        #print line_time,'line_time'
        #print '-----------'
        return line_time

    def get_daq_frequency(self,onepps):
        """
        time: in seconds
        triggers: in counts
        """
        #print 'abouttocalculatefrequency'
        #print onepps
        #print self.lastonepps
        #print self.passedonepps

        if not self.passedonepps:
            #print 'nopassedonepps'
            self.calculatedfrequency = self.defaultfrequency
            self.lastoneppspoll = onepps
            return

        else:
            self.calculatedfrequency = (onepps - self.lastoneppspoll)/float(self.passedonepps)
            #print self.calculatedfrequency

        self.lastoneppspoll = onepps

        if  self.calculatedfrequency <= 0:
            #print 'failedusingdefault'
            self.calculatedfrequency = self.defaultfrequency
        self.debug_freq.write(str(self.calculatedfrequency) + '\n')

    def extract(self,line):
        """Search for triggers in a set of lines"""

        line = line.split()

        # remember this!
        # 92328FE2 00 3D 00 3E 00 00 00 00 915E10CF 034016.021 060180 V 00 0 +0055
        # triggers r0 f0 r1 f1 r2 f2 r3 f3 onepps   gpstime    gpsdte        correction
        #  0        1  2  3  4  5  6  7  8    9       10        11    12 13 14 15

        # remember here that get_time returns seconds!
        # we need nanoseconds here, so that we can add the pulses le 
        # and fe times        

        #TODO: correct for delayed onepps switch
        #TODO: correct for trigger ouunt rollover
        onepps        = int(line[9],16)
        trigger_count = int(line[0],16)
        # correct for triggercount rollover
        if trigger_count < self.lasttriggercount:
            trigger_count += int(0xFFFFFFFF) # counter offset


	self.trigger_count = trigger_count
	#print trigger_count- self.lasttriggercount, 'extract triggercount diff'

      
	switched_onepps = False
        if onepps != self.lastonepps:
            self.passedonepps += 1
            # poll every x lines for the frequency

            self.pollcount += 1
            switched_onepps = True
            if not self.pollcount%5:
                self.get_daq_frequency(onepps)
                self.pollcount = 0
                self.passedonepps = 0

        self.prevlast_onepps = self.lastonepps
        self.lastonepps = onepps
        linegpstime = self.get_gps_time(line[10],line[15])
        
        if linegpstime == self.lastlinegpstime and switched_onepps:
            #print 'delayed onepps'
            self.linetime = self.get_time(trigger_count,prevlast=True)

        else:
            self.linetime = self.get_time(trigger_count)

        #print self.linetime, ' extract: self.linetime'
        self.triggerflag = int(line[1],16) & BIT7    

	self.lastlinegpstime = linegpstime
        #self.rel_linetime  = self.get_rel_time(trigger_count,onepps)
 
        if self.triggerflag:
            #print 'trigger',line 
            self.ini = False
            
            # a new trigger!o we have to evaluate the last one and get the new pulses
            self.lastchan0re = self.chan0re
            self.lastchan0fe = self.chan0fe
            self.lastchan1re = self.chan1re
            self.lastchan1fe = self.chan1fe
            self.lastchan2re = self.chan2re
            self.lastchan2fe = self.chan2fe
            self.lastchan3re = self.chan3re
            self.lastchan3fe = self.chan3fe
            self.order_and_cleanpulses()
            extracted_pulses = (self.lasttriggertime,self.chan0,self.chan1,self.chan2,self.chan3) 

            # UNCOMMENT FOR DEBUG
            #i = 0
            #for item in extracted_pulses[1:]:
            #     if item:
            #         i += 1

            #if not i:
            #    print line
            #    print extracted_pulses 

            # the pulses of the last event are done!
            # now the new beginning event
            self.lasttriggertime = self.linetime

            self.chan0re = []  
            self.chan0fe = []
            self.chan1re = []
            self.chan1fe = []
            self.chan2re = []
            self.chan2fe = []
            self.chan3re = []
            self.chan3fe = []         

            self.calculate_edges(line)

            # UNCOMMENT FOR DEBUG
            #print self.chan0re
            #print self.chan0fe
            #print self.chan1re
            #print self.chan1fe
            #print self.chan2re
            #print self.chan2fe
            #print self.chan3re
            #print self.chan3fe           


            if self.pulsefile:
                self.pulsefile.write(extracted_pulses.__repr__() + '\n')

	    self.lastlinetime = self.linetime       
            #self.lastrellinetime = self.rel_linetime
            self.lasttriggercount = trigger_count 

            return extracted_pulses
 
        else:    
            # we do have a previous trigger and are now adding more pulses to the event
            #print 'notrigger',line

            if self.ini:
                self.lastonepps = int(line[9],16)


            else:
                counter_diff = 0
                counter_diff = (self.trigger_count - self.lasttriggercount)
                #print counter_diff, counter_diff > int(0xffffffff)
                if counter_diff > int(0xffffffff):
	            counter_diff -= int(0xffffffff)

                counter_diff = counter_diff/self.calculatedfrequency
                #print counter_diff,counter_diff*1e9,' edges diff'
		
                self.calculate_edges(line,counter_diff=counter_diff*1e9)
                # UNCOMMENT FOR DEGUB
                #print 'Adding more pulses' 
                #print self.chan0re
                #print self.chan0fe
                #print self.chan1re
                #print self.chan1fe
                #print self.chan2re
                #print self.chan2fe
                #print self.chan3re
                #print self.chan3fe
        
	self.lastlinetime = self.linetime       
        #self.lastrellinetime = self.rel_linetime
        self.lasttriggercount = trigger_count 


    def close_file(self):
        self.pulsefile.close()          



# trigger on a set of extracted pulses and look for decayed muons
# this trigger builds from DAQ triggers....


class DecayTriggerBase:
    """
    Feel free to write your own muon decay trigger! It just needs to inherit from this 
    Base class
    """

    def __init__(self,triggerpulses,chan3softveto):
        #self.triggerwindow = 2000 # 20microseconds
        #self.triggerwindow =  20000 # 20 microseconds 
        self.triggerwindow = 20e-6
        self.lasttriggerpulses = triggerpulses
        self.chan3softveto = chan3softveto


    def trigger(self,thistriggerpulses):
        """
        Implement this method with your own trigger logic!
        """ 
        raise NotImplementedError("This feature has to be implemented first!")
 



class DecayTriggerSimple(DecayTriggerBase):
    """
    This trigger is designed to decide wether to adjacent triggers
    occur within 20microseconds
    """   


    def trigger(self,thistriggerpulses):
     
           # decay time based only on cpld clock!
           if self.chan3softveto:
               if (not self.lasttriggerpulses[4]) & (not thistriggerpulses[4]):
	           # we simply subtract two trigger times!
                   decaytime0 = thistriggerpulses[0] - self.lasttriggerpulses[0]
	
                   if decaytime < self.triggerwindow:
                       self.lasttriggerpulses = thistriggerpulses
                       if decaytime > 0:
                            self.lasttriggerpulses = thistriggerpulses
                            return decaytime

                       else:
                           self.lasttriggerpulses = thistriggerpulses

               else:
                   self.lasttriggerpulses = thistriggerpulses


           else:
               decaytime = thistriggerpulses[0] - self.lasttriggerpulses[0]
               if decaytime < self.triggerwindow:
                   self.lasttriggerpulses = thistriggerpulses
                   if not decaytime < 0:
                       return decaytime
	

               else:
                   self.lasttriggerpulses = thistriggerpulses 


class DecayTriggerSingle(DecayTriggerBase):
    """
    No coincidence settings are chosen,
    just looking for two pulses in 20 microsecs
    The implementation is the same like DecayTriggerSimple,
    but the coincidence settings must be chosen differently
    """   


    def trigger(self,thistriggerpulses):
     
           # decay time based only on cpld clock!
           if self.chan3softveto:
               if (not self.lasttriggerpulses[4]) & (not thistriggerpulses[4]):
	           # we simply subtract two trigger times!
                   decaytime0 = thistriggerpulses[0] - self.lasttriggerpulses[0]
	
                   if decaytime < self.triggerwindow:
                       self.lasttriggerpulses = thistriggerpulses
                       if decaytime > 0:
                            self.lasttriggerpulses = thistriggerpulses
                            return decaytime

                       else:
                           self.lasttriggerpulses = thistriggerpulses

               else:
                   self.lasttriggerpulses = thistriggerpulses


           else:
               decaytime = thistriggerpulses[0] - self.lasttriggerpulses[0]
               if decaytime < self.triggerwindow:
                   self.lasttriggerpulses = thistriggerpulses
                   if not decaytime < 0:
                       return decaytime
	

               else:
                   self.lasttriggerpulses = thistriggerpulses

class DecayTriggerThoroughDeprecated(DecayTriggerBase):
    """
    We demand a second pulse in the same channel where the muon got stuck
    Pulses must not be farther away than the triggerwindow
    """   


    def trigger(self,thistriggerpulses):
     
           # decay time based only on cpld clock!
           if self.chan3softveto:
               if (not self.lasttriggerpulses[4]) & (not thistriggerpulses[4]):
                   # get the channel with the stuck muon
                   muonstuckpulse = self.lasttriggerpulses[0]
                   muonstuckchannel = False
                   for chan in enumerate(self.lasttriggerpulses[1:]):
                        for pulse in chan[1]:
                            nanosecpulse = pulse[1]
                            if nanosecpulse + self.lasttriggerpulses[0] > muonstuckpulse:
                                muonstuckpulse = nanosecpulse + self.lasttriggerpulses[0]
                                muonstuckchannel = chan[0]

                   trigger = False
                   if muonstuckchannel:
                       for chan in enumerate(thistriggerpulses):
                           if chan[0] == muonstuckchannel + 1:
                               if chan[1]:
                                   trigger = True

                           else:
                               if chan[1]:
                                   trigger = False

               if trigger:
                   decaytime = (thistriggerpulses[0] + thistriggerpulses[muonstuckchannel + 1][0][0]) - (self.lasttriggerpulses[0] + self.lasttriggerpulses[muonstuckchannel + 1][0][0])
                   if decaytime < self.triggerwindow:
                       self.lasttriggerpulses = thistriggerpulses
                       if decaytime > 0:
                            self.lasttriggerpulses = thistriggerpulses
                            return decaytime

                       else:
                           self.lasttriggerpulses = thistriggerpulses

               else:
                   self.lasttriggerpulses = thistriggerpulses

           else:    
              # get the channel with the stuck muon
              muonstuckpulse = self.lasttriggerpulses[0]
              muonstuckchannel = False
              for chan in enumerate(self.lasttriggerpulses[1:]):
                   for pulse in chan[1]:
                       nanosecpulse = pulse[1]
                       if nanosecpulse + self.lasttriggerpulses[0] > muonstuckpulse:
                           muonstuckpulse = nanosecpulse + self.lasttriggerpulses[0]
                           muonstuckchannel = chan[0]


              trigger = False
              if muonstuckchannel:
                  for chan in enumerate(thistriggerpulses):
                      if chan[0] == muonstuckchannel + 1:
                          if chan[1]:
                              trigger = True

                      else:
                          if chan[1]:
                              trigger = False
              if trigger:
                   decaytime = (thistriggerpulses[0] + thistriggerpulses[muonstuckchannel + 1][0][0]) - (self.lasttriggerpulses[0] + self.lasttriggerpulses[muonstuckchannel + 1][0][0])
                   if decaytime < self.triggerwindow:
                      self.lasttriggerpulses = thistriggerpulses
                      if decaytime > 0:
                          self.lasttriggerpulses = thistriggerpulses
                          return decaytime

                      else:
                          self.lasttriggerpulses = thistriggerpulses

              else:
                  self.lasttriggerpulses = thistriggerpulses


class DecayTriggerThorough(DecayTriggerBase):
    """
    We demand a second pulse in the same channel where the muon got stuck
    Pulses must not be farther away than the triggerwindow
    """   


    def trigger(self,thistriggerpulses):
        """
        Hardcoded use of chan 1,2,3!!
        """ 
       
        mupulse1 = bool(self.lasttriggerpulses[2]) 
        mupulse2 = bool(self.lasttriggerpulses[3])
        mupulse3 = bool(self.lasttriggerpulses[4])
        mutime   = self.lasttriggerpulses[0]

        epulse1  = bool(thistriggerpulses[2])
        epulse2  = bool(thistriggerpulses[3])
        epulse3  = bool(thistriggerpulses[4])
        etime    = thistriggerpulses[0]

        decaytime = 0
        # the electron might decay in chan1 or chan2
        if (not epulse3) and (not mupulse3):

            if epulse2 and mupulse2 and mupulse1:
                decaytime = etime - mutime

            elif epulse1 and mupulse1 and (not mupulse2):
                decaytime = etime - mutime

            else:
                decaytime = 0
	
            if (decaytime > 0) and (decaytime < self.triggerwindow):
                self.lasttrigerpulses = thistriggerpulses
                return decaytime

        else:
            self.lasttriggerpulses = thistriggerpulses
            return None
		

        
 
 


if __name__ == '__main__':

    #line = '6B00BC12 00 30 00 31 00 00 00 00 00000002 000000.000 000000 V 00 8 +0000'
    	
    import sys
    import numpy

    #data = open('virtenv/muonic/build/lib/muonic/daq/simdaq.txt')
    data = open(sys.argv[1])
    extractor = PulseExtractor()
    while True:
        line = data.readline()
        if not line:
	    break
        try:
            extractor.extract(line)
            #print extractor.extract(line)
            #print extractor.chan1fe
        except (ValueError,IndexError):
            #print 'some error', line

            pass 



