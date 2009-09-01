import sys
import gzip
from operator import itemgetter

files = sys.argv[1:]

BIT0_4 = 31
BIT5 = 1 << 5
BIT7 = 1 << 7

# For DAQ status
BIT0 = 1 # 1 PPS interrupt pending
BIT1 = 1 << 1 # Trigger interrupt pending
BIT2 = 1 << 2 # GPS data possible corrupted
BIT3 = 1 << 3 # Current or last 1PPS rate not within range

#freq = 41666667.0
freq = 25000000.0
MINI_TICK = 1.0/(freq * 32)


def time_to_seconds(time, correction):
    '''
    Convert hhmmss,xxx string int seconds since day start
    '''
#    print time,correction
    tfields = time.split(".")
    t = tfields[0]
    secs_since_day_start = int(t[0:2])*3600+int(t[2:4])*60+int(t[4:6])
    evt_time = secs_since_day_start + int(tfields[1])/1000.0+int(correction)/1000.0
    return round(evt_time)


class Pulse(object):
    def __init__(self, channel):
        self.channel = channel
        self.valid = False
        self.wait_falling = False
    
    def rise(self, time):
        self.wait_falling = True
        self.rise_time = time

    def fall(self, time):
        if self.wait_falling:
            self.fall_time = time
            self.valid = True
            self.wait_falling = False
            print "TOT",self.channel,(time - self.rise_time) * 1e9
    
    def invalidate(self):
        self.valid = False

    def width(self):
        if self.valid:
            return self.fall_time - self.rise_time
        else:
            raise ValueError()

def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

@coroutine
def muon_finder(muon=(0,1,2,3),decay=3):
    def reset(d):
        print "Reset"
        for key in d.iterkeys():
            d[key] = 0.
    
    def all_channels_set(channels, muon):
        for ch in muon:
            if channels[ch] == 0.:
                return False
        return True

    channels = {0:0.,1:0.,2:0.,3:0.}
    lastpulse_time = 0.
    while True:
        pulse = (yield)
        ch = pulse[0]
        time = pulse[1]
        print "Dt:",time - lastpulse_time
        if 0 < time - lastpulse_time < 100.e-9 or lastpulse_time == 0.:
            channels[ch] = time
            lastpulse_time = time
            print channels
        else:
            reset(channels)
            channels[ch] = time
            lastpulse_time = time
            continue
        if all_channels_set(channels, muon):
            print "MUON"
            pulse = (yield)
            print "got pulse",pulse
            ch = pulse[0]
            time = pulse[1]
            if ch == decay and 0 < time - lastpulse_time < 20.e-6:
                print "Decay:", (time - lastpulse_time) * 1e6
            else:
                reset(channels)
                channels[ch] = time
                lastpulse_time = time

verbose = True
pulse0 = Pulse(0)
pulse1 = Pulse(1)
pulse2 = Pulse(2)
pulse3 = Pulse(3)

pulse_counter = 0
muon_decay = muon_finder(muon=(0,3,2,1),decay=1)
#muon_decay = muon_finder(muon=(0,2,1),decay=1)
last_onepps_count = 0

for filename in sys.argv[1:]:
    if filename.endswith('.gz'):
        f = gzip.open(filename)
    else:
        f = open(file)
    for line in f:
        if verbose: print line
        fields = line.rstrip("\n").split(" ")
        # Ignore malformed lines
        if len(fields) != 16:
            continue
        #Ignore everything that is not trigger data
        if len(fields[0]) != 8:
            continue
        # Check if GPS data is valid
        if fields[12] != "A":
            print "GPS data not valid"
            continue
        #Another check, sometimes lines are mixed,
        #try if we can convert the last field to an int
        try:
            int(fields[len(fields)-1])
        except ValueError:
            continue
#        Check if error bits are set
        if fields[14] != "0":
            err = int(fields[14],16)
            if (err & BIT0) != 0:
                print '1 PPS interrupt pending'
            if (err & BIT1) != 0:
                print 'Trigger interrupt pending'
            if (err & BIT2) != 0:
                print 'GPS data corrupt'
            if (err & BIT3) != 0:
                print '1PP rate not within range'
            print line
            continue
        trigger_count = int(fields[0],16)
        onepps_count = int(fields[9],16)
        if onepps_count != last_onepps_count:
            print "PPS:",onepps_count - last_onepps_count
            last_onepps_count = onepps_count

        trigger = (int(fields[1],16) & BIT7) != 0

        time = fields[10]
        correction = fields[15]
        seconds = time_to_seconds(time,correction)+(trigger_count - onepps_count)/freq
        line_time = seconds + (trigger_count - onepps_count)/freq
        if trigger:
            if verbose: print "Trigger: %10.12f"%(line_time,)
            pulse0.invalidate()
            pulse1.invalidate()
            pulse2.invalidate()
            pulse3.invalidate()
       
        re0 = int(fields[1],16)
        if re0 & BIT5 != 0:
            time = line_time + (re0 & BIT0_4) * MINI_TICK
            pulse0.rise(time)
            if verbose: print "0> %10.12f"%(time,)
        fe0 = int(fields[2],16)
        if fe0 & BIT5 != 0:
            time = line_time + (fe0 & BIT0_4) * MINI_TICK
            pulse0.fall(time)
            if verbose: print "0< %10.12f"%(time,)
        re1 = int(fields[3],16)
        if re1 & BIT5 != 0:
            time = line_time + (re1 & BIT0_4) * MINI_TICK
            pulse1.rise(time)
            if verbose: print "1> %10.12f"%(time,)
        fe1 = int(fields[4],16)
        if fe1 & BIT5 != 0:
            time = line_time + (fe1 & BIT0_4) * MINI_TICK
            pulse1.fall(time)
            if verbose: print "1< %10.12f"%(time,)
        re2 = int(fields[5],16)
        if re2 & BIT5 != 0:
            time = line_time + (re2 & BIT0_4) * MINI_TICK
            pulse2.rise(time)
            if verbose: print "2> %10.12f"%(time,)
        fe2 = int(fields[6],16)
        if fe2 & BIT5 != 0:
            time = line_time + (fe2 & BIT0_4) * MINI_TICK
            pulse2.fall(time)
            if verbose: print "2< %10.12f"%(time,)
        re3 = int(fields[7],16)
        if re3 & BIT5 != 0:
            time = line_time + (re3 & BIT0_4) * MINI_TICK
            pulse3.rise(time)
            if verbose: print "3> %10.12f"%(time,)
        fe3 = int(fields[8],16)
        if fe3 & BIT5 != 0:
            time = line_time + (fe3 & BIT0_4) * MINI_TICK
            pulse3.fall(time)
            if verbose: print "3< %10.12f"%(time,)

        pulses = []

        if pulse0.valid:
            width = pulse0.width() * 1e9
            if verbose: print "0:",width
            pulses.append((0,pulse0.rise_time))
            pulse0.invalidate()
        if pulse1.valid:
            width = pulse1.width()
            if verbose: print "1:",width
            pulses.append((1,pulse1.rise_time))
            pulse1.invalidate()
        if pulse2.valid:
            width = pulse2.width()
            if verbose: print "2:",width
            pulses.append((2,pulse2.rise_time))
            pulse2.invalidate()
        if pulse3.valid:
            width = pulse3.width()
            if verbose: print "3:",width
            pulses.append((3,pulse3.rise_time))
            pulse3.invalidate()

        pulses.sort(key=itemgetter(1))
        for pulse in pulses:
            muon_decay.send(pulse)
