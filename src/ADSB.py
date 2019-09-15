import ADSBdecode
import asyncio
import socket

class ADSB_TCPConnection(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

class ADSB_BaseStation(asyncio.Protocol):
	#ADSB_BaseStation(server-ip,server-port)
	def __init__(self, ip, port):
		if(type(ip) is not str and type(port) is not int):
			raise TypeError
    	#check validity of ip and port
		socket.inet_aton(ip)
		if(port > 65535 or port < 0):
			raise "Port is not in range 0-65535"
		self.SERVER = {"IP" : ip , "PORT" : port}
	
		
		
