from bluetooth import *
import subprocess
import smtplib
import re
import pickle
import textwrap
import threading
from Xlib import X, display
d = display.Display()
s = d.screen()
root = s.root
pos = (0,0)

def moveMouseDelta(x,y):
    global pos
    if abs(x) > 90 or abs(y) > 90:
	return
    pos = (pos[0]+x, pos[1]+y)
    pos = (pos[0] if pos[0] >= 0 else 0,pos[1] if pos[1] >= 0 else 0)
    root.warp_pointer(pos[0],pos[1])
    d.sync()
moveMouseDelta(pos[0],pos[1])


class PCSide:
    def __init__(self):
        self.server_socket=BluetoothSocket(RFCOMM)
        self.server_socket.bind(("", 11)) #max port no is 30!..
        self.server_socket.listen(1)
        self.sendLock = threading.Lock()
    def recv(self, length):
        data = ''
        recd = 0
        while (recd < length):
            buf = self.client_socket.recv(length-recd)
            recd += len(buf)
            data += buf
        return data
    def send(self, data):
        self.client_socket.send(data)
    def listen(self):
        self.client_socket, self.address = self.server_socket.accept()
    def recvMsg(self):
        lenStr = self.recv(9)
        print "LenStr: ", lenStr
        l = int(lenStr.lstrip('0'))
        data = self.recv(l)
        return pickle.loads(data)
    def sendMsg(self,text):
        with self.sendLock:
            text = pickle.dumps(text)
            l = str(len(text))
            s = ('0'*(9-len(l))) + str(l)
            s = s + text
            print "Sending: ",s
            self.send(s)

    def __del__(self):
        self.server_socket.close()
        self.client_socket.close()

ps = PCSide()
print "Server Running!"
ps.listen()
print "Connection Accepted!"

try:
    while True:
	data = ps.recvMsg()
	xPos, yPos,zPos = [],[],[]
	for x in data:
	    xPos.append(x['x'])
	    yPos.append(x['y'])
	    zPos.append(x['z']) 
	try:
	    xAvg,yAvg,zAvg = sum(xPos)/len(xPos),sum(yPos)/len(yPos),sum(zPos)/len(zPos)
	except Exception,e:
	    xAvg = yAvg = zAvg = 0

	moveMouseDelta(xAvg/2,yAvg/2)
except Exception, e:
    print "Error!!!!!",e