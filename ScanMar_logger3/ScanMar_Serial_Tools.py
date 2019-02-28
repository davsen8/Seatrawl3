import serial
import time
import threading
try:
    import queue

except:
    import Queue as queue
import io
import ScanMar_Nmea as SMN
import pynmea2
from collections import OrderedDict


DEFAULT_RATE = 1   # scans per second
SIMULATOR = False

########################################################################################
#  SERIAL PORT STD READER CLASS
# non threaded version  reads data from port when asked via next method
# initialization
#
# for linux
# ser.port = "/dev/ttyS2"
# for windows
# ser.port ="COM1"
#
# Possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call
#
# ser.timeout = None          #blocking read when using radline
# ser.timeout = 0             #non-block read


# ser.get_settings()
# ser.apply_settings(d)
########################################################################################
class Read_Serial_Stuff(threading.Thread):

    def __init__(self ,ser, queue):

        self.queue = queue
#        self.ser = serial.Serial()  # Create a serial com port access instance
        self.ser = ser
        self.set_default()  # other than port and baud
#        self.set_settings(settings)
        self.StartTime = 0

        self.wait = True
        self.pause = False
        self.scan = dict()

        self.shutdown = False
        threading.Thread.__init__(self)


    def set_default (self):  #Defaults as specified
#        DEFAULT_COM = "COM8"
#        DEFAULT_BAUD = 9600

#        self.ser.port = DEFAULT_COM
#        self.ser.baudrate = DEFAULT_BAUD
        self.ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
        self.ser.parity = serial.PARITY_NONE  # set parity check: no parity
        self.ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
        self.ser.timeout = 5  # timeout block read
        self.ser.xonxoff = True  # disable software flow control
        self.ser.rtscts = False  # disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 2  # timeout for write

#    def set_settings (self,settings): # over-ride defaults,dict keys must match serial parameters
#        for x in settings:
#            self.ser.x =  settings[x]

    def open_Port(self):
        try:
            self.ser.open()
        except serial.SerialException as e :
#            print "error open serial port: "+self.ser.port+" " + str(e)
             return(False)
        self.flush()
        return (True)

    def close_Port(self):
        try:
            self.ser.close()
        except:
            pass

    def flush (self):
        if self.ser.isOpen():
            self.ser.flushInput()
            time.sleep(0.05)
            line = self.ser.readline() # ensure a full line is in buffer by discarding any stub

    def start_data_feed(self):
        self.flush()
        self.wait = False

    def pause_data_feed(self):
        self.wait = True

    def shut_down(self):
        self.pause_data_feed()
        self.shutdown = True
        time.sleep(0.05)   # avoid pulling the rug out to quick

    def close_port(self):
        if self.is_port_open():
            self.close_Port()

    def run (self):
        if (self.is_port_open() == False):
            self.open_Port()
        self.ser.flush()

        retrys = 0
        while not self.shutdown:
            line = self.next()
            if line != '' and not self.wait :  # if we are paused just waste the record, but keep reading
                self.queue.put(line)
                retrys = 0
            else :
                if not self.wait:
                    retrys = retrys +1
#                time.sleep (0.05)

            if retrys > 100:
                line = "FINISHED"   # need a better code, but this is what archived file uses for now
                self.queue.put(line)
                retrys = 0  # we don't want to hang or stop trying, we want the main program to tell us what to do

        self.queue.put("FINISHED")
        self.close_port()
        return

# when changed to python 3.65 from 2.8 started getting issue on shutdown causing exception
# relating to overlapping read io issue or port already closed,,  the try-except is to swallow the
# error message as a QAD fix for now.. DRS
    def next(self):

        line= ''

#        if not self.shutdown:
        if self.is_port_open () :
#                try:
                    line = self.ser.readline().decode()
#                except :
#                    pass

        return (line)


    def is_port_open(self):
        return (self.ser.isOpen())

# *** END OF Read_Serial_Stuff Class ******************


##########################################################################
# READS DATA FROM A FILE :PASS 1 LINE at a atime back via the next method

class Read_File_Stuff(threading.Thread):
    """
        A thread class that will read a line , output that number to queue and sleep
        noet that to start the htread call start function ,,, DONOT create a local start or you'll oveeride Threads
    """

    def __init__(self, filename, q):
        self.filename = filename
        self.q = q
        self.shutdown = False
        self.wait = True
        threading.Thread.__init__(self)

    def run(self):
        while self.wait:
            pass

#        self.fp = io.open(self.filename,"rb")
#        self.sio = io.TextIOWrapper(self.fp,newline = '\r\n')


        with open(self.filename) as self.fp:
             if not self.wait:

                for line in self.fp:
                    if not self.shutdown:
                        if "GLL" in line:
                            time.sleep(1.0)   # emulate 1 second data bursts spaced on the GLL block String
                        self.q.put(line)
#                        time.sleep(0.01) # this is just to make the feed more readable and not blow through it
                    else:
                        self.q.put("FINISHED")
                        self._close_source()
                        return()
        self.q.put("FINISHED")
#            print "thread says by by"

    def start_data_feed(self):
        self.wait = False

    def pause_data_feed(self):
        self.wait = True

    def _close_source(self):
        self.fp.close()

    def flush (self):   # dummy to keep compatible with serial feed
        pass

    def shut_down(self):
        self.shutdown = True
##########################################################################################################
class DataGen_que(threading.Thread):

    def __init__(self, Parent,Source,info,BQueue):
        self.parent = Parent
        self.source = Source
        self.BlockQueue = BQueue



        self.myQueue = queue.Queue()

        if self.source != "SERIAL":
            self.datafile = info
            self.Reader_Thread = Read_File_Stuff(self.datafile, self.myQueue)
        else:
            self.settings = info
            self.Reader_Thread = Read_Serial_Stuff(self.settings, self.myQueue)

        self.CurrentBlock = {}
        self.CurrentBlock["HAVE-GLL"] = False
        self.CurrentBlock["NEWBLOCK"] = True
        self.CurrentBlock["NEXTGLL"] = False

#        scanner = SMN.SCAN_TOOLS()

        self.status=''
        self.shutdown = False
        self.feed_on = False
        msg = ""
        self.scanner = SMN.SMN_TOOLS()

# built into start the thread..
        self.Reader_Thread.start()

        threading.Thread.__init__(self)



    def next_block(self):
        NextGLL = False
        block = OrderedDict ()
        abort_block = False
        # where going to scan until we get the full data cycle, delineated by a GLL
        # try and get some data, if cant get it in ?? seconds, some thing is funny
        tries = 0
        while (tries < 60) and self.feed_on:
            if not self.myQueue.empty():
                tries = 0
                line = self.myQueue.get()
                if line != "FINISHED" and line != "WAITING":
                    try:
                        msg = pynmea2.parse(line)
                    except pynmea2.nmea.ChecksumError:   # this needs more thought on handling
                        print ("Checksum issue")
                        block["OK"] = False
                        self.status = "CHECKSUM_ERROR"
                        abort_block = True
                        continue

#                    print "YES MSG=",msg

                    self.scanner.process_message_new(msg)
                    x=self.scanner.current["SENSOR"]

                    if x == "SM2":
                        if "SM2" not in block:
                                block["SM2"] = OrderedDict()
                        y = self.scanner.current["SENSOR_ELEMENT"]
                        block[x][y] = msg
#                        print "BLOCK xy = ",msg

                    else:
                        block[x] = msg

                        if x == "GLL" :
#                            print ">>>> GLL", block["GLL"].latitude, block["GLL"].lat

                            if self.CurrentBlock["HAVE-GLL"]:  # copy forward
                                block["GLL"] = self.CurrentBlock["NEXTGLL"]
                                self.CurrentBlock["NEXTGLL"] = msg
                                self.CurrentBlock["NEWBLOCK"] = True
                                NextGLL=  True

                            else:  # start a new block
                                self.CurrentBlock["NEWBLOCK"] = False
                                self.CurrentBlock["HAVE-GLL"] = True
                                self.CurrentBlock["NEXTGLL"] = msg
                else:
                    block["OK"] = False
                    block["REASON"] = line
                    self.status = line
                    return (block)


            else:
                    time.sleep(0.1)
                    tries = tries + 1

            if NextGLL:
                break

        if tries == 60:
            block["OK"] = False
            block["REASON"] = "EMPTY_QUEUE"
            self.status = "EMPTY_QUEUE"
        else:
            block["OK"]= True
            self.status = "OK"

        return(block)


#    def next(self):
#        block = self.next_block()
#        return(block)

    def run (self):
        while not self.shutdown:
            if self.feed_on:
                block = self.next_block()
                if block["OK"] :
                    self.BlockQueue.put(block)
                else:
                    break

    def close_DataSource(self):
#        if self.status != "FINSHED":
            self.feed_on = False
            self.flush()
            self.Reader_Thread.shut_down()
            self.parent.flash_status_message("DATA SOURCE STOPPED & CLOSED")

            self.shutdown = True

    def flush(self):  # the mutex is to make sure it is thread safe since clear is 'under the hood'
        self.Reader_Thread.flush()
        with self.myQueue.mutex:
            self.myQueue.queue.clear()

    def pause_data_feed (self):
        self.feed_on = False
        self.Reader_Thread.pause_data_feed()
        self.parent.flash_status_message("DATA SOURCE PAUSED")

    def start_data_feed (self):
        self.Reader_Thread.start_data_feed()
        self.feed_on = True
        self.parent.flash_status_message("DATA SOURCE (Re)Started")