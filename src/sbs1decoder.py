import time

class SBSMessage:
    def __init__(self, msg):
        fields = [x.strip() for x in msg.split(',')]

        assert fields[0] == 'MSG', "SBS packet not MSG"

        assert fields[1].isdigit(), "Wrong SBS MSG Transmission Type"
        self.TransmissionType = int(fields[1])
        self.SessionID = fields[2]
        self.AircraftID = fields[3]
        self.HexID = fields[4]
        self.FlightID = fields[5]
        self.DateMessageGenerated = fields[6]
        self.TimeMessageGenerated = fields[7]
        self.DateMessageLogged = fields[8]
        self.TimeMessageLogged = fields[9]

        self.Callsign = fields[10]
        self.PressureAltitude = fields[11]
        self.GroundSpeed = fields[12]
        self.Track = fields[13]
        self.Latitude = fields[14]
        self.Longitude = fields[15]
        self.VerticalRate = fields[16]
        self.Squawk = fields[17]

        self.Alert = fields[18]
        self.Emergency = fields[19]
        self.SPI = fields[20]
        self.IsOnGround = fields[21]

        self.Timestamp = time.time()
