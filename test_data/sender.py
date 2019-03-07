# from : http://eli.thegreenplace.net/2009/07/30/setting-up-python-to-work-with-the-serial-port/
# simple sender use with http://com0com.sourceforge.net/
# http://www.magsys.co.uk/comcap/onlinehelp/null_modem_emulator_com0com.htm

#############################################################################
# NOTE  IF YOU HAVE ISSUES NOT GETTING DATA LOWER THE SIZE OF THE FIFO BUFFERS 
# IN THE WINDOWS HARDWARE SETUP FOR THE SERIAL PORTS UNDER ADVANCED SETTINGS
#############################################################################

import serial
import time
import msvcrt # built-in module
import sys

class DataGen2(object):
	def __init__(self, FileName,init=50):
		self.data = self.init = init
		self.FileName = FileName
		self.f = open(self.FileName,"r")
		print ("File opened")

	def next(self):
		line=self.f.readline()
		return line

	def close_infile(self):
		print ("closing file")
		self.f.close()

	def rewind(self):
		self.f.seek(0)

def on_send_timer(datagen,ser) :
	line = datagen.next()
	if "GLL" in line:
		time.sleep(1.0)
	if line !=[] :
		x = ser.write(line.encode())
		return line
	else:
		return ([])


def kbfunc():

	return msvcrt.getwch() if msvcrt.kbhit() else '0'

def main() :
	if len(sys.argv) != 3:
		print ("supply port and data file name")
		quit()
	print (sys.argv[0], sys.argv[1], sys.argv[2])


	FileName= sys.argv[2]


#	FileName = "scanmar_rs_trimmed.log"

	port = str(sys.argv[1])
	Nseconds = 0.02
	print ("reading",FileName," from port ",port)
	datagen = DataGen2(FileName)
	print ("trying for serial port ",port)
	try: 
		ser = serial.Serial(port, 4800)
	except serial.SerialException as e:
		print ("error opening serial port: "+port+" " + str(e))
		return(False)
	print ("port open")

	print (" Press p to pause ; g to go ; l to loop ; f faster ; s slower ; z toggle silent mode ; q to quit gracefully")


	x = "x"
	paused = True
	kk = ''
	loop = False
	silent = False
	while x !="" :
	
		kk = kbfunc()

		if kk == 'g':
			paused=  False
		if kk == 'p':
			paused = True
		if kk == 'l':
			loop = True
		if kk == 'z':
			silent = not silent
		if kk  == 'q':
			break
		if kk == 'f':


			if Nseconds < 0.00001: 
				Nseconds = 0.0
				sys.stdout.write("\a") # plays a beep to say your at limit
			else:
				Nseconds = Nseconds - 0.005
			print (Nseconds)
			
		if kk == 's':
			Nseconds = Nseconds + 0.005
			print (Nseconds)
	
		if Nseconds > 0:	
			time.sleep(Nseconds)
		if not paused:
			x = on_send_timer(datagen,ser)
			if not silent:
				print (x, end='')
			if x =='' and loop:
				datagen.rewind()
		

	datagen.close_infile()

	ser.close()
	print ('bye - port closed')

if __name__ == '__main__':
		main()
