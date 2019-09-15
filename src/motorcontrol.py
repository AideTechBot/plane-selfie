import sys
import os
from time import sleep

AZ_MIN = 1.00
AZ_MAX = 2.01
EL_MIN = 1.50
EL_MAX = 2.05
AZ_GPIO = 23
EL_GPIO = 4
msPerCycle = 10.0

# SAFETY BOUNDS
sAZ_MIN = 0.099
sAZ_MAX = 0.205
sEL_MIN = 0.149
sEL_MAX = 0.206

def aim_at(azimuth, elevation):
    try:
        assert 0.0 <= azimuth <= 360.0, "Azimuth needs to be 0-360 degrees"
        assert elevation <= 90.0, "Elevation needs to be less than 90 degrees"

        #fractions for az and el
        decaz = 1.0 - (float(azimuth) / 360.0)
        decel = float(elevation) / 90.0

        #pulse len for az and el
        azplen = AZ_MIN + (decaz * (AZ_MAX - AZ_MIN))
        elplen = EL_MIN + (decel * (EL_MAX - EL_MIN))

        az_dutycycle =  azplen / msPerCycle
        el_dutycycle = elplen / msPerCycle
        if (float(elevation) < 0.0):
            el_dutycycle = EL_MIN / 10
            elplen = EL_MIN

        assert sAZ_MIN <= az_dutycycle <= sAZ_MAX, "Azimuth dutycycle outside of safe bounds."
        assert sEL_MIN <= el_dutycycle <= sEL_MAX, "Elevation dutycycle outside of safe bounds."

        os.system(f"echo \"{AZ_GPIO}={az_dutycycle}\" > /dev/pi-blaster")
        os.system(f"echo \"{EL_GPIO}={el_dutycycle}\" > /dev/pi-blaster")
    except:
        os.system(f"echo \"release {AZ_GPIO}\" > /dev/pi-blaster")
        os.system(f"echo \"release {EL_GPIO}\" > /dev/pi-blaster")

if __name__ == "__main__":
    az, el = 0, 0
    while 1:
        aim_at(az % 360, el % 90)
        print(az % 360,el % 90)
        az += 10
        el += 10
        sleep(1)
