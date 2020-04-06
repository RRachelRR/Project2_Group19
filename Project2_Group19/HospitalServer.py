import base64
import time
from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import json
import threading
from threading import Lock
from threading import Condition
from pip._vendor.distlib.compat import raw_input
import mysql.connector

# Login to database
try:
	mydb = mysql.connector.connect(
	    host="localhost",
	    user="root",
	    passwd="password123",
	    database="testdb"
	)
except:
	print("Error logging into database")
	
mycursor = mydb.cursor()


# Thread that handles discovery
class BroadcastThread(threading.Thread):
    def __init__(self, funcpoint, args):
        threading.Thread.__init__(self)
        self.funcpoint = funcpoint
        self.args = args

    def run(self):
        print("Starting Broadcast Thread " + self.name)
        self.funcpoint(self.args)

    
# Thread that handles robots
class RobotThread(threading.Thread):
    def __init__(self, funcpoint, args):
        threading.Thread.__init__(self)
        self.funcpoint = funcpoint
        self.args = args

    def run(self):
        print("Starting Robot Thread " + self.name)
        self.funcpoint(self.args)


# Thread that handles staff
class StaffThread(threading.Thread):
    def __init__(self, funcpoint, args):
        threading.Thread.__init__(self)
        self.funcpoint = funcpoint
        self.args = args

    def run(self):
        print("Starting Staff Thread " + self.name)
        self.funcpoint(self.args)


# Thread that handles servers
class ServerThread(threading.Thread):
    def __init__(self, funcpoint, args):
        threading.Thread.__init__(self)
        self.funcpoint = funcpoint
        self.args = args

    def run(self):
        print("Starting Server Thread " + self.name)
        self.funcpoint(self.args)


# AES parameter
modeAES = AES.MODE_CFB  # Cipher Mode


# Encrypt and decode are not exactly taken from this link, but were inspired by this code
# https://stackoverflow.com/questions/14179784/python-encrypting-with-pycrypto-aes


def encryptAES(message, key, iv):
    # If message is not in bytes makes it bytes
    if type(message) is str:
        bytemessage = message.encode()
        message = bytemessage
    encryptObject = AES.new(key, modeAES, iv)  # Object to encrypt
    cipherText = encryptObject.encrypt(message)  # encrypt message
    return base64.b64encode(cipherText)  # returns a string


def decryptAES(ciphertext, key, iv):
    # If ciphertext is not string makes it a string
    if type(ciphertext) is not str:
        strtext = base64.b64decode(ciphertext)
        ciphertext = strtext
    decryptObject = AES.new(key, modeAES, iv)  # Object to decrypt
    message = decryptObject.decrypt(ciphertext)  # decrypt message
    return message.decode()  # return string

#initialise broadcast
def broadcastSock():
    broadcastSocket = socket(AF_INET, SOCK_DGRAM)
    broadcastSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    broadcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    return broadcastSocket


def broadcast(broadcastSock):
    while True:
        broadcastSock.sendto(("127.0.0.1, 12000, 12001, 12002").encode('utf-8'), ('<broadcast>', 8888))

# opens socket to communicate with other servers on socket 12000
def openSock():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(5)
    print('Server is ready to receive')
    return serverSocket


# opens socket to communicate with other servers on socket 12000
def openStaffSock():
    serverPort = 12001
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(5)
    print('Server is ready to receive')
    return serverSocket


# opens socket to communicate with other servers on socket 12002
def openServerSock():
    serverport1 = 12002
    serversocket1 = socket(AF_INET, SOCK_STREAM)
    serversocket1.bind(('', serverport1))
    serversocket1.listen(5)
    print('Ready to talk to other servers')
    return serversocket1


# creates a new thread to handle incoming server messages
def listenToNewServer(sock):
    while True:
        serverConnectionSocket, addr = sock.accept()
        print('Got new server connection')
        thread = ServerThread(listenToServer, serverConnectionSocket)
        thread.start()


# handles messages coming in from another server
def listenToServer(sock):
    while True:
        try:
            input = sock.recv(1024).decode()
            if not input:  # sometimes a closed connection sends empty messages
                break
        except ConnectionResetError:
            print('Server connection failed')
            return

        input2 = json.loads(input)
        if int(input2[0]) == 3:  # checks if robot is online on this server
            if input2[1] in robotsOnline:
                answe = str(0)
            else:
                answe = str(1)
                
        elif int(input2[0]) == 5:
            servers.append(input2[1])

        sock.send(answe.encode())


# creates a new thread to handle incoming server messages
def listenToNewStaff(sock):
    while True:
        staffConnectionSocket, addr = sock.accept()
        print('Got new staff connection')
        thread = StaffThread(listenToStaff, staffConnectionSocket)
        thread.start()


# handles messages coming in from staff
def listenToStaff(sock):
    staffName = ""
    sessionAESKey = ""  # symmetric encryption key
    sessionAESIv = ""  # initial value for randomness

    try:
        # Get public RSA Key from staff
        clientExportedPublicRSAKey = sock.recv(2048)  # Key as in a file/string
        clientPublicRSAKey = RSA.import_key(clientExportedPublicRSAKey)  # Key as object
        cipherObjectRSA = PKCS1_OAEP.new(clientPublicRSAKey)  # Object to encrypt and decrypt with key

        # Generate AES Key and IV
        sessionAESKey = get_random_bytes(16)
        sessionAESIv = get_random_bytes(16)

        # Send AES session key and IV to staff
        cipheredSessionAESKey = cipherObjectRSA.encrypt(sessionAESKey)  # encrypted AES session key
        cipheredSessionAESIv = cipherObjectRSA.encrypt(sessionAESIv)  # encrypted AES IV
        sock.send(cipheredSessionAESKey)
        sock.send(cipheredSessionAESIv)

        while True:
            input1 = sock.recv(1024).decode()
            if not input1:  # sometimes after a connection closes empty messages come through
                break
            input = json.loads(input1)
            if int(input[0]) == 0:  # receiving staff username
                staffName = input[1]

                sql_query = "SELECT EXISTS(SELECT * FROM staff_tb WHERE name = %s)" # check if staff exists in db
                mycursor.execute(sql_query, (staffName,))
                query_result = mycursor.fetchone()   # either 1 or 0 
                
                if query_result[0] == 0:    
                    mes = 'Username does not exist'
                    sock.send(mes.encode())
                    return
             
                sql_query = "SELECT salt FROM staff_tb WHERE name = %s" # get salt from database
                mycursor.execute(sql_query, (staffName,))
                query_result = mycursor.fetchone()

                staffSalt = encryptAES(query_result[0], sessionAESKey, sessionAESIv)  # encrypt salt for that robot
                sock.send(staffSalt)  # send salt


            elif int(input[0]) == 1:  # receiving login password
                staffInfo = input[1]
                staffName = staffInfo[0]
                encryptedStaffPassword = staffInfo[1]
                staffPassword = decryptAES(encryptedStaffPassword.encode(), sessionAESKey,
                                           sessionAESIv)  # decrypt hashed password
                mes = json.dumps([str(3), staffName])

                # check if staff name in database
                sql_query = "SELECT EXISTS(SELECT * FROM staff_tb WHERE name = %s)"
                mycursor.execute(sql_query, (staffName,))
                query_name = mycursor.fetchone()   

                # fetch password from database
                sql_query = "SELECT hash_pword FROM staff_tb WHERE name = %s" 
                mycursor.execute(sql_query, (staffName,))
                query_passwd = mycursor.fetchone()
                

                if len(servers) != 0:
                    check = loginCheck(servers, 12002, mes)  # check if staffmember is already online somewhere
                else:
                    check = 1  # if there is only one server the player can't be online on another one
                if staffName in staffOnline:  # player is already online on this server
                    print('Staffmember is already online on this server')
                    answ = 2
                elif int(check) == 0:  # player is already online on another server
                    print('Staffmember is already online on another server')
                    answ = 4
                elif query_name[0] == 0:  # player doesn't exist
                    print('Staffmember does not exist')
                    answ = 3
                elif staffPassword.encode() == query_passwd[0].encode():  # Player is allowed to log in
                    staffOnline[staffName] = 0
                    print(staffName + " has logged in")
                    answ = 1
                else:  # Staffmember is in the system but the combination of name and password is not correct
                    print('Id or Password incorrect')
                    answ = 0
                if int(answ) == 1:
                    sock.send(json.dumps([str(1)]).encode())
                else:
                    sock.send(json.dumps([str(answ)]).encode())  # if not send error code
                if answ == 2 or answ == 0 or answ == 3 or answ == 4:
                    return
            

            elif int(input[0]) == 2:  # receiving update on this robots location
                addRoom = input[1]

                #Update status of room to 1 (needs cleaning)
                sql_query = "UPDATE  room_tb SET status = 1 WHERE id = %s"
                mycursor.execute(sql_query, (addRoom,))
                mydb.commit()  

                roomsToClean.append(addRoom)
                print("Added room " + str(addRoom))
                sock.send(json.dumps([str(21)]).encode())
                staffOnline.pop(staffName)


    except ConnectionResetError:  # when player closes program, they log out
        print(staffName + " has closed connection")
        robotsOnline.pop(staffName)  # remove staff from online list
        return


# handles messages coming in from another player
def listenToRobot(sock):
    robotId = ""
    sessionAESKey = ""  # symmetric encryption key
    sessionAESIv = ""  # initial value for randomness

    try:
        # Get public RSA Key from robot
        clientExportedPublicRSAKey = sock.recv(2048)  # Key as in a file/string
        clientPublicRSAKey = RSA.import_key(clientExportedPublicRSAKey)  # Key as object
        cipherObjectRSA = PKCS1_OAEP.new(clientPublicRSAKey)  # Object to encrypt and decrypt with key

        # Generate AES Key and IV
        sessionAESKey = get_random_bytes(16)
        sessionAESIv = get_random_bytes(16)

        # Send AES session key and IV to robot
        cipheredSessionAESKey = cipherObjectRSA.encrypt(sessionAESKey)  # encrypted AES session key
        cipheredSessionAESIv = cipherObjectRSA.encrypt(sessionAESIv)  # encrypted AES IV
        sock.send(cipheredSessionAESKey)
        sock.send(cipheredSessionAESIv)

        while True:
            input1 = sock.recv(1024).decode()
            if not input1:  # sometimes after a connection closes empty messages come through
                break
            input = json.loads(input1)
            if int(input[0]) == 0:  # receiving robotId
                robotId = input[1]

                sql_query = "SELECT EXISTS(SELECT * FROM robo_tb WHERE id = %s)" # check if robot exists in db
                mycursor.execute(sql_query, (robotId,))
                query_result = mycursor.fetchone()   # either 1 or 0 

                if query_result[0] == 0:  
                    mes = 'RobotId does not exist'
                    sock.send(mes.encode())
                    return

                sql_query = "SELECT salt FROM robo_tb WHERE id = %s" # get salt from database
                mycursor.execute(sql_query, (robotId,))
                query_result = mycursor.fetchone()

                robotSalt = encryptAES(query_result[0], sessionAESKey, sessionAESIv)  # encrypt salt for that robot
                sock.send(robotSalt)  # send salt
            elif int(input[0]) == 1:  # receiving login password
                robotInfo = input[1]
                robotName = robotInfo[0]
                encryptedRobotPassword = robotInfo[1]
                robotPassword = decryptAES(encryptedRobotPassword.encode(), sessionAESKey,
                                           sessionAESIv)  # decrypt hashed password
                mes = json.dumps([str(3), robotId])

                # check if robot id in database
                sql_query = "SELECT EXISTS(SELECT * FROM robo_tb WHERE id = %s)"
                mycursor.execute(sql_query, (robotId,))
                query_id = mycursor.fetchone()   

                # fetch password from database
                sql_query = "SELECT hash_pword FROM robo_tb WHERE id = %s" 
                mycursor.execute(sql_query, (robotId,))
                query_passwd = mycursor.fetchone()

                if len(servers) != 0:
                    check = loginCheck(servers, 12002, mes)  # check if robot is already online somewhere
                else:
                    check = 1  # if there is only one server the robot can't be online on another one
                if robotId in robotsOnline:  # robot is already online on this server
                    print('Robot is already online on this server')
                    answ = 2
                elif int(check) == 0:  # robot is already online on another server
                    print('Robot is already online on another server')
                    answ = 4
                elif query_id[0] == 0:  # Robot doesn't exist
                    print('Robot id does not exist')
                    answ = 3
                elif robotPassword.encode() == query_passwd[0].encode():  # Robot is allowed to log in
                    robotsOnline[robotId] = lastPositions[robotId]
                    print(robotId + ' was last in room ' + str(robotsOnline[robotId]))
                    answ = 1
                else:  # Robot is in the system but the combination of name and password is not correct
                    print('Id or Password incorrect')
                    answ = 0
                if (int(answ) == 1):  # if robot is allowed to log in, send him last known position
                    sock.send(json.dumps([str(1), robotsOnline[robotId]]).encode())
                else:
                    sock.send(json.dumps([str(answ)]).encode())  # if not send error code
                if answ == 2 or answ == 0 or answ == 3 or answ == 4:
                    return

            elif int(input[0]) == 2:  # receiving update on this robots location
                robotstat = input[1]
                print("Receiving update from robot " + str(robotstat[0]))
                if robotstat[1] == 0:
                    print(str(robotstat[0]) + " is currently not busy")
                    sql_query = "UPDATE  robo_tb SET curr_room = %s WHERE id = %s" # update robot's location in db
                    mycursor.execute(sql_query, (robotstat[1],robotstat[0],))
                    done = False
                    while done == False:
                        roomMutex.acquire()
                        try:
                            if len(roomsToClean) != 0:
                                print("Rooms currently needing cleaning: " + str(len(roomsToClean)))
                                newRoom = roomsToClean.pop(0)
                                answer = json.dumps([11, newRoom])
                                print("Sending robot to " + str(newRoom))

                                sql_query = "UPDATE  robo_tb SET curr_room = %s WHERE id = %s" 	# update location in db
                                mycursor.execute(sql_query, (newRoom,robotstat[0],))

                                lastPositions[robotstat[0]] = newRoom
                                robotsOnline[robotstat[0]] = newRoom
                                done = True
                            else:
                                print("No rooms currently need cleaning!")
                                robotsOnline[robotstat[0]] = 0
                                answer = json.dumps([13, 0])
                                done = True
                        finally:
                            roomMutex.release()
                else:
                    print(str(robotstat[0]) + ' is in room ' + str(robotstat[1]))
                    answer = json.dumps([12])
                    lastPositions[robotstat[0]] = robotstat[1]
                    robotsOnline[robotstat[0]] = robotstat[1]
                sock.send(answer.encode())
                robotsOnline.pop(robotstat[0])
                print(str(len(robotsOnline)) + " Robots are left")
    except ConnectionResetError:  # when robot closes program, they log out
        print(robotId + " has closed connection")
        robotsOnline.pop(robotId)  # remove robot from online list
        return


# creates a new thread to handle incoming robot messages
def listenNewConnection(sock):
    while True:
        connectionSocket, addr = sock.accept()
        print('Got new robot connection')
        thread = RobotThread(listenToRobot, connectionSocket)
        thread.start()


# sends message to all servers to check if robot is already logged in
# returns 0 if robot is already logged in, 1 otherwise
def loginCheck(servlist, port, message):
    for serv in servlist:
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((serv, port))
            sock.send(message.encode())
            result = sock.recv(1024).decode()
            sock.shutdown(SHUT_RDWR)
            sock.close()
            if int(result) == 0:
                return result
        except ConnectionResetError:
            print('Humorous Server Connection Error Message')
        except ConnectionRefusedError:
            print('Humorous Server Offline Message')
    return result



lastPositions = {'1': 0, '2': 0, '3': 0, '4': 0}  # last known positions of robots
roomsToClean = [5,2]
#roomsToClean.append(query_room[0])
robotsOnline = {}  # Robots currently online
staffOnline = {} # staff currently online
servers = []  # Servers connected to the network
IP = "127.0.0.1"


sbroadcastSocket = socket(AF_INET, SOCK_DGRAM)
sbroadcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sbroadcastSocket.settimeout(3)
sbroadcastSocket.bind(('', 8888))
print("Listening for other servers")
while True:
    try:
        data = sbroadcastSocket.recv(1024)
        servers.append(data[0])
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((data[0], data[3]))
        sock.send(IP.encode())
        result = sock.recv(1024).decode()
        sock.shutdown(SHUT_RDWR)
        sock.close()
        break
    except timeout:
        print("No active servers")
        break
sbroadcastSocket.close()




#servNum = raw_input("Enter number of servers you want to link: ")
#if int(servNum) != 0:
    #for x in range(1, int(servNum) + 1):
     #   servIp = raw_input("Enter IP address for server number " + str(x) + ": ")
     #   servers.append(servIp)
print("Other servers in network: " + str(len(servers)))
serverSocket = openSock()  # Socket to communicate with robots
syncSocket = openServerSock()  # Socket to communicate with other servers
staffSocket = openStaffSock()
broadSocket = broadcastSock()
roomMutex = Lock()
thread1 = RobotThread(listenNewConnection, serverSocket)  # Thread listening to new robots
thread1.start()
thread2 = ServerThread(listenToNewServer, syncSocket)  # Thread listening to other servers
thread2.start()
thread3 = StaffThread(listenToNewStaff, staffSocket)  # Thread listening to other servers
thread3.start()
thread4 = BroadcastThread(broadcast, broadSocket) # thread broadcasting IP
thread4.start()