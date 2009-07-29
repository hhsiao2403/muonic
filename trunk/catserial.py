import serial
import sys
import time

def main():
    try:
        port = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, bytesize=8,parity='N',stopbits=1,timeout=1,xonxoff=True)
    except serial.SerialException, e:
        print e.message
        sys.exit(1)
    port.write("NM 1\r")
    while True:
#        port.write("View\rV1\r")
#        port.write("View\rV3\r")
#        port.write("TH\r")
#        port.write("DG\r")
#        time.sleep(1)
        while port.inWaiting():
            print port.readline().strip()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
