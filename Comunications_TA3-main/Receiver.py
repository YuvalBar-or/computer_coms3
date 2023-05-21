import socket
import time
import os

class Receiver:
    def __init__(self, filename, host, port, id_1, id_2):
        self.filename = filename
        self.host = host
        self.port = port
        self.chunk_size = 1024
        #log for statistics
        self.log = []
        #ids for XOR auth operation
        self.xor = bin(int(id_1)^int(id_2))[2:]
        self.auth = str(self.xor).encode()
        self.conn = None
        self.addr = None
        self.filesize = 0
        self.s = None
        self.max = 0
        self.ended = 0

    def run(self, flag):
        #open file for writing
        with open(self.filename, 'wb') as f:
            #initilize socket
            if flag == 0:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s = s
            else:
                s = self.s
            #bind & listen
            if flag == 0:
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                self.conn = conn
                self.addr = addr
            else:
                conn = self.conn
                addr = self.addr
            with conn:
                print('Connected by', addr)
                #recive file size & make first and second half sizes
                if flag == 0:
                    file_size_str = conn.recv(self.chunk_size)
                    conn.sendall(self.auth)
                    file_size = int(file_size_str.decode())
                    self.filesize = file_size
                else:
                    file_size = self.filesize

                first_half_size = file_size//2
                total_recived = 0
            
                #server loop
                #start timer for fist half sent
                start_time = time.time()
                while True:
                    #recive data and write to file
                    data = conn.recv(self.chunk_size)
                    f.write(data)
                    #total recived increased
                    total_recived+=len(data)
                    #if finshed first half
                    if total_recived == first_half_size:

                        size = os.path.getsize(self.filename)
                        print(f'first half recived - size of : {size}')
                        #send auth
                        conn.sendall(self.auth)
                        #end timer
                        end_time_first_half = time.time()
                        #total first half time
                        first_half_time = end_time_first_half - start_time
                        #appending data to log
                        self.log.append(first_half_time)
                    #if second half finished
                    if total_recived == file_size:
                        size = os.path.getsize(self.filename)
                        print(f'seoond half recived - size of : {size}')
                        #send auth
                        conn.sendall(self.auth)
                        #end timer
                        end_second_half_time = time.time()
                        second_half_time = end_second_half_time - end_time_first_half
                        #append second half total time
                        self.log.append(second_half_time)
                        print('file recived')
                        #response for if to send again or end
                        response = conn.recv(self.chunk_size)
                        if response.decode() == 'RESEND':
                            
                            conn.sendall(b'OK')
                            
                            #rerun
                            self.run(1)
                            if self.ended == 1:
                                break
                        elif response.decode() == 'BYE':

                            conn.sendall(b'OK')
                            conn.close()
                            self.max = max(self.log)
                            time.sleep(2*self.max)
                            s.close()
                            self.ended = 1
                            #for statatistics
                            avg_first = 0
                            avg_second = 0
                            count = 0
                            total = 0
                            #run throgh log and make avgs, totals
                            print(' ')
                            print('Statistics:')
                            print('*************************************************************************')
                            for i in range(len(self.log)):
                                if i % 2 == 0:
                                    print(f'first half iteration {int((i+1)/2)+1} sent successfully in {self.log[i]} seconds.')
                                    avg_first+=self.log[i]
                                else:
                                    print(f'second half iteration {int(i/2)+1} sent successfully in {self.log[i]} seconds.')
                                    avg_second+=self.log[i]

                                count+=1
                                if i == 0:
                                    total+=self.log[i]
                                else:
                                    total+= self.log[i-1]+self.log[i]
                            print('*************************************************************************')
                            print(f'first half avg: sent successfully in {avg_first/(count/2)} seconds.')
                            print(f'second half avg: sent successfully in {avg_second/(count/2)} seconds.')
                            print(f'total avg: sent successfully in {total/(count)} seconds.')
                            print('*************************************************************************')
                            break

def main():

    filename = "received_file.txt"
    host = "127.0.0.1"  # self ip
    port = 9999 # port 9999 free

    r1 = Receiver(filename, host, port, '332307073', '214329633')
    r1.run(0)


if __name__ == "__main__":
    main()