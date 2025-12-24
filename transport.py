import socket
import json
import threading
class Transport:
    def __init__(self,my_address,node_instance):

        self.my_address=my_address
        self.node=node_instance

        #creating the UDP socket
        #AF_INET= Internet Protocol(IP) SOCK_STREAM= Universal Datagram Protocol(UDP)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #bind the socket (telling the OS "the address is mine")
        self.socket.bind(self.my_address)
        #------starting the thread to listen
        t= threading.Thread(target=self.listen_internal,daemon=True)
        t.start()
    def listen_internal(self):#listens infinitely for incoming messages
        while True:
            try:
                data,addr= self.socket.recvfrom(4096) #buffer size =4096
                data_string=data.decode("utf-8")
                data_dict=json.loads(data_string)
                self.node.handle_message(data_dict,addr)
            except Exception as e:
                print(f"Error in listener: {e}")
    def send_message(self,target_address,message):
        #convert the dict to json to bytes
        msg_bytes=json.dumps(message).encode("utf-8")
        #send data
        self.socket.sendto(msg_bytes,target_address)
