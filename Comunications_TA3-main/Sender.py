import socket
import time
import string
import random
import os


class Sender:
    def __init__(self, host, port, filename, id_1, id_2):
        self.host = host
        self.port = port
        self.filename = filename
        #random size between 3MB - 6MB file size of chars
        mb_size = random.randint(3,6)*1024*1024
        self.filesize = mb_size
        self.create_random_file(mb_size)
        self.s = None
        self.xor = bin(int(id_1)^int(id_2))[2:]
        self.expected_auth = str(self.xor).encode()
        

    def create_random_file(self, mb_size):
        with open("{}".format(self.filename), "w") as f:
            count = 1
            while os.path.getsize(self.filename) < mb_size:
                f.write(random.choice(string.ascii_letters))
                if(count%50 == 0):
                    count = 0
                    f.write('\n')
                count+=1
                
                

    def send_file(self, flag):
        first_half = self.filesize // 2 
        # 1.	At first, you’ll read the file you’ve created.
        with open(self.filename, 'rb') as f:
            data = f.read()
            first_data = data[:first_half]
            second_data = data[first_half:]

        # 2.	Create a TCP Connection between the sender and receiver.
        if flag == 0:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_TCP, socket.TCP_CONGESTION, b'reno')
            s.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            self.s = s
        else:
            s = self.s
        
        #send length of file
        if flag == 0:
            
            s.sendall(str(self.filesize).encode())
            auth = s.recv(1024)
            
            if auth == self.expected_auth:
                print('Recived ack on file size')
        # send first half of the file
        s.sendall(first_data)
        print("Sent first half of file:")

        # receive authentication for first half
        auth = s.recv(1024)
        if auth == self.expected_auth:
            print(f"Authentication received for first half: {auth}")

        #change CC algorithm
        s.setsockopt(socket.SOL_TCP, socket.TCP_CONGESTION, b'cubic')
        print("CC algorithm changed to cubic:")
        # send second half of the file
        s.sendall(second_data)
        print("Sent second half of file:")
        

        # receive authentication for second half
        auth = s.recv(1024)
        if auth == self.expected_auth:
            print(f"Authentication received for second half: {auth}")
        print("Sent second half of file:")
        size = os.path.getsize(self.filename)
        print(' ')
        print(f'total file sent - size of : {size}')
        # ask user if they want to send the file again
        send_again = input("Do you want to send the file again? (y/n) ")
        if send_again.lower() == 'y':
            # notify the receiver
            s.sendall(b"RESEND")
            print("Notified receiver to send again.")
            auth = s.recv(1024)
            # change back CC algorithm
            self.s.setsockopt(socket.SOL_TCP, socket.TCP_CONGESTION, b'reno')
            print("CC algorithm changed back to reno.")
            print(' ')
            self.send_file(1)
        else:
            # say bye to the receiver and close the connection
            s.sendall(b"BYE")
            print("Sent exit message to receiver.")
            auth = s.recv(1024)
            s.close()


if __name__ == "__main__":
    sender = Sender('127.0.0.1', 9999, 'random.txt','332307073', '214329633')
    sender.send_file(0)
