
import sys
import operator

from functools import reduce	
def checksum(nmea_str):
        return reduce(operator.xor, map(ord, nmea_str), 0)

def main() :
    if len(sys.argv) != 2:
        print ("supply string")
        quit()
	
    print (sys.argv[0], sys.argv[1])
    thestring= sys.argv[1].lstrip()
    print ('|'+thestring+'|')
    print (hex(checksum(thestring)))

if __name__ == '__main__':
		main()

        