from motorcontrol import aim_at
from ADSBdecode import *
from ADSB import *
import threading
from sbs1decoder import SBSMessage
from math import *
from geopy.distance import great_circle
from helper import *
import socket
import time
import heapq
import sys

#constants
#distances are in km
Eradius = 6371.0
tau = 2 * pi
Ecircum = Eradius * tau

#returns the Elevation of the object where
#distance is the length of the arc that connect the two positions on the earth
#altitude is the height above the earth
#both in km
def calcEL(distance, altitude):

	#degree between both positions relative to the center of the earth
	theta = (distance/Ecircum) * tau

	#degree between Pos A and the center of the earth relative to Pos B
	phi = pi - pi/2 - theta

	#measure of how much of the objects altitude is below the horizon
	below =  (Eradius/sin(phi)) - Eradius

	#if its below the horizion return 0 degrees
	if below >= altitude:
		return 0.0

	#if theta is 0 then hes directly above us
	if theta <= 0.0:
		return 90.0

	#distance in a straight line from Pos A to Pos B
	straightLine = Eradius * tan(theta)

	#shortest distance between object A and object B
	a = straightLine
	b = (altitude - below)
	y = (pi - phi)
	distAB = sqrt((a**2 + b**2) - (2*a*b*cos(y)))

	#now calculate the El angle
	a = (altitude - below)**2 - distAB**2 - straightLine**2
	b = -2.0 * distAB * straightLine
	El = degrees(acos(a/b))

	return El


# returns the azimuth to the plane
def calcAZ(north,station,plane):
	#A is the north pole
	#B is the station
	#C is the plane
	BA = (north[0]-station[0],north[1]-station[1])
	BC = (plane[0]-station[0], plane[1]-station[1])
	
	#calculate the two parts of the division
	numerator = dotproduct(BA,BC)
	denominator = norm(BA) * norm(BC)
	
	#return theta
	return 360.0 + (degrees(acos(numerator/denominator)) - 180.0)
	
planeDict = {}
def main():
    '''
    HOUSE = (47, 47)
    PLANE = [(48, 47),10.0]
    distance = great_circle(HOUSE,PLANE[0]).km
    prin calcEL(distance,PLANE[1])
    print calcAZ((90.0,0.0),(HOUSE[0], HOUSE[1]), (PLANE[0][0], PLANE[0][1]))
    '''
    #try initiating the socket
    try:
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.connect(('localhost',30003))
    except:
        print("Something went wrong when creating the socket.")
        sys.exit(1)

    while(1):
        #catch the data
        data = ""
        try:
            data = cli.recv(1024).decode('utf-8')
        except:
            print("Connection closed unexpectantly")
            sys.exit(1)
        #print(data)
        if "\n" in data:
            data = data.split("\n")
            data = filter(None, data)
            for msg in data:
                sbsmsg = SBSMessage(msg)
#                print(sbsmsg.Longitude, sbsmsg.Latitude)
                if(sbsmsg.TransmissionType == 3 and sbsmsg.Longitude.strip()
                    != "" and sbsmsg.Latitude.strip() != "" and
                    sbsmsg.PressureAltitude.strip() != ""):
                    if(sbsmsg.HexID not in planeDict):
                        planeDict[sbsmsg.HexID] = [ sbsmsg ]
                    else:
                        planeDict[sbsmsg.HexID].insert(0, sbsmsg)

def get_lock():
    if(len(planeDict.keys()) == 0):
        return "No planes"
    planeICAO, msgHistory = max(planeDict.items(), key = lambda x: len(set(x[1])))
    if(time.time() - msgHistory[0].Timestamp > 30.0):
        del planeDict[planeICAO]
        return get_lock()
    else:
        return planeICAO
        

def footToKM(foot):
    return foot * 0.0003048

def update():
    print("Starting locking mechanism...")
    while(1):
        lockedPlane = get_lock()
        if(lockedPlane != "No planes"):
            print(f"Locked on: {lockedPlane}")
            lockedPlane = planeDict[lockedPlane][0]
            time.sleep(1)

            HOUSE = (43.473513, -80.539802)
            NORTH = (90.0, 0.0)
            PLANE = (float(lockedPlane.Latitude), float(lockedPlane.Longitude))
            PLANE_ALT = footToKM(float(lockedPlane.PressureAltitude))
            distance = great_circle(HOUSE,PLANE).km
            el = calcEL(distance, PLANE_ALT)
            az = calcAZ(NORTH, HOUSE, PLANE)

            print(az,el)
            aim_at(az,el)

if __name__ == '__main__':
    try:
        thread1 = threading.Thread(target=main)
        thread2 = threading.Thread(target=update)
        thread1.start()
        thread2.start()
    except KeyboardInterrupt:
        pass
    thread1.join()
    thread2.join()

    print("Quitting")
