
import socket

class ClusterInfo:
    def __init__(self):
        self.PORT = 2000
        self.IP = socket.gethostname() 

    def Print():
        print(f"-----------------------\nPORT: {self.PORT} \nIP: {self.IP}-----------------------\n")