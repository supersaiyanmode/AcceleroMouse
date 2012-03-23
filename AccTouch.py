import btsocket as socket
import sensor
import appuifw
import e32
import thread
import pickle

toSend = []

class PhoneClient:
    def __init__(self):
        self.pcMac = '00:1F:E2:F2:9F:5E'
        self.client_socket=socket.socket(socket.AF_BT,socket.SOCK_STREAM)
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
        
    def sendMsg(self,obj):
        text = pickle.dumps(obj)
        l = str(len(text))
        s = ('0'*(9-len(l))) + str(l)
        s = s + text
        self.send(s)

    def connect(self):
        self.client_socket.connect((self.pcMac,11))
    def recvMsg(self):
        lenStr = self.recv(9)
        print "LenStr: ", lenStr
        l = int(lenStr.lstrip('0'))
        data = self.recv(l)
        return pickle.loads(data)
    def __del__(self):
        self.client_socket.close()

pc = PhoneClient()
try:
    pc.connect()
except Exception, e:
    print "Unable to connect!"
    exit(0)


accelerometer = sensor.AccelerometerXYZAxisData(data_filter=sensor.LowPassFilter())
counter = 0

def my_callback():
    global counter
    global toSend
    try:
	if not counter:
	    accelerometer.stop_listening()
	    pc.sendMsg(toSend)
	    toSend = []
	    accelerometer.start_listening()
    except Exception,e:
	print e
	quit()
    toSend.append({"type":"xyz","x":accelerometer.x, "y":accelerometer.y, "z":accelerometer.z})
    counter = (counter + 1)%10

def quit():
    accelerometer.stop_listening()
    print "Exiting Accelorometer"

appuifw.app.exit_key_handler = quit
accelerometer.set_callback(data_callback=my_callback)
accelerometer.start_listening()
raw_input()

