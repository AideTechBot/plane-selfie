from math import *

#constants
NZ = 15.0
charset = '#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######'


#convert input hex into bin and fill zero in front of the str
def hex2bin(hexstr):
  scale = 16
  num_of_bits = len(hexstr)*log(scale, 2)
  binstr = bin(int(hexstr, scale))[2:].zfill(int(num_of_bits))
  return binstr

#converts input binary to int
def bin2int(binstr):
  return int(binstr, 2)

#because reasons
def mod(x,y):
	return x % y

#calculates the dot product of two tuples
def dotproduct(x,y):
	product = 0
	if len(x) != len(y):
		raise IndexError
	for n in range(0,len(x)):
		product = (x[n] * y[n]) + product
	return product

#calculates the norm of a tuple
def norm(x):
	return sqrt(dotproduct(x,x))

#denotes the number of longitude zones function
def NL(lat):
	if type(lat) is not float:
		raise TypeError

	a = 1.0 - cos(pi/(2.0*NZ))
	b = cos((pi/180.0)*lat) ** 2.0
	c = acos(1.0 - (a/b))
	d = floor((2.0*pi)/c)
	
	return d

#converts longitude and latitude to xyz coordinates relative to the earths center
def toxyz(latitude, longitude):
	e_radius = 6371000
	latitude = radians(latitude)
	longitude = radians(longitude)
	x = e_radius * (cos(latitude) * cos(longitude))
	y = e_radius * (cos(latitude) * sin(longitude))
	z = e_radius * (sin(latitude))

	return (x,y,z)

#decodes the planes callsign
def decodecallsign(msg):
	msgbin = hex2bin(msg)
	databin = msgbin[32:88]   # python start from 0

	# get the callsign part
	csbin = databin[8:]

	# convert callsign by charset
	callsign = ''
	callsign += charset[ bin2int(csbin[0:6]) ]
	callsign += charset[ bin2int(csbin[6:12]) ]
	callsign += charset[ bin2int(csbin[12:18]) ]
	callsign += charset[ bin2int(csbin[18:24]) ]
	callsign += charset[ bin2int(csbin[24:30]) ]
	callsign += charset[ bin2int(csbin[30:36]) ]
	callsign += charset[ bin2int(csbin[36:42]) ]
	callsign += charset[ bin2int(csbin[42:48]) ]

	# clean string, remove spaces and marks, if any.
	chars_to_remove = ['_', '#']
	cs = callsign.translate(None, ''.join(chars_to_remove))
	return cs
	
#decodes position from two odd and even ADS-B messages
#input is two lists that look like this
#[msg1, timestamp1], [ms2,timestamp2]
def decodepos(packet1, packet2):
	#timestamps for the packets
	ts1 = packet1[1]
	ts2 = packet2[1]

	#converts msg1 and msg2 to binary
	msg1 = hex2bin(packet1[0])
	msg2 = hex2bin(packet2[0])

	##check if bit 54 is odd or even
	if not ((msg1[53] == "0" and msg2[53] == "1") or (msg1[53] == "1" and msg2[53] == "0")):
		##if not crash
		raise TypeError
	result = []
	
	#swap them if the first one is odd
	swap = 0
	if msg1[53] == "1":
		temp = msg1
		msg1 = msg2
		msg1 = temp
		swap = 1
	
	#put it into decimal
	max = 131072.0
	CPR_LAT_EVEN = float(int(msg2[54:71],2)) / max
	CPR_LONG_EVEN = float(int(msg2[72:88],2)) / max
	CPR_LAT_ODD = float(int(msg1[54:71],2)) / max
	CPR_LONG_ODD = float(int(msg1[72:88],2)) / max
	
	
	#latitude index j
	j = floor(((59.0 * CPR_LAT_EVEN) - (60.0 * CPR_LAT_ODD)) + 0.5)	
	
	#generate two constants
	D_LAT_EVEN = 360.0/(4.0 * NZ)
	D_LAT_ODD = 360/(4.0 * NZ - 1.0)

	#calculate relative latitudes
	LAT_EVEN = D_LAT_EVEN * (mod(j,60.0) + CPR_LAT_EVEN)
	LAT_ODD = D_LAT_ODD * (mod(j,59.0) + CPR_LAT_ODD)
	
	#take into account the southern hemisphere
	if LAT_EVEN >= 270.0:
		LAT_EVEN = LAT_EVEN - 360
	if LAT_ODD >= 270.0:
		LAT_ODD = LAT_ODD - 360
	
	if ts1 > ts2 and not swap:
		return LAT_EVEN
	else:
		return LAT_ODD
