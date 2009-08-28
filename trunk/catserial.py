import serial
import sys
import time
import os
from optparse import OptionParser
from datetime import datetime
import gzip

class FileWriter(object):
    
    def __init__(self,path):
        if os.path.exists(path):
            raise ValueError('File %s already exists'%path)
        if path.endswith('.gz'):
            self.file = gzip.open(path,'w')
        else:
            self.file = open(path,'w')
    
    def writeln(self, line):
        self.file.write(line)


def main():
    thresholds = (50,150,50,50)
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    default_filename = 'daq_' + now + '.txt.gz'
    parser = OptionParser()
    parser.add_option('-o','--outfile',dest='outfile',
                       default=default_filename,help='Path of output file')
    (options, args) = parser.parse_args(sys.argv[1:])
    try:
        port = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,parity='N',stopbits=1,timeout=1,xonxoff=True)
    except serial.SerialException, e:
        print e.message
        sys.exit(1)
    print "Successfully connected to serial port"
    writer = FileWriter(options.outfile)
    # setup simple muon telesope
    port.write('RB\r')
    port.write('TI\r')
    port.write('CD\r')
    port.write('WC 00 07\r') # Singles with channels 0,1,2
#    port.write('WC 00 03\r') # Singles with channels 0,1
    port.write('WC 01 00\r')
    port.write('WC 02 04\r') # gate width 4 clockticks (96 ns)
    port.write('WC 03 00\r')
    port.write('WT 01 00\r') # TMC delay= 2 clockticks (48 ns)
    port.write('WT 02 02\r')
    # Set thresholds
    for i,thresh in enumerate(thresholds):
        port.write('TL ' + str(i) + ' ' + str(thresh) + '\r')
    port.write('TL\r')
    port.write('DC\r')
    port.write('DG\r')
    port.write('DS\r')
    port.write('DT\r')
    port.write('BA\r')
    port.write('TH\r')
    port.write('CE\r')

    while True:
        while port.inWaiting():
            line = port.readline()
            writer.writeln(line)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
