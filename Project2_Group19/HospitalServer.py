import base64
import time
from socket import*
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES,PKCS1_OAEP
from Crypto.Random import get_random_bytes
import json
import threading
from threading import Lock
from threading import Condition
from pip._vendor.distlib.compat import raw_input

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
        sock.send(answe.encode())


# creates a new thread to handle incoming server messages
def listenToNewStaff(sock):
    while True:
        staffConnectionSocket, addr = sock.accept()
        print('Got new staff connection')
        thread = StaffThread(listenToStaff, staffConnectionSocket)
        thread.start()

#handles messages coming in from staff
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
            if not input1:   # sometimes after a connection closes empty messages come through
                break
            input = json.loads(input1)
            if int(input[0]) == 0:  # receiving staff username
                staffName = input[1]
                if staffName not in staffPasswords:
                    mes = 'Username does not exist'
                    sock.send(mes.encode())
                    return
                mes = staffPasswords[staffName]
                staffSalt = encryptAES(mes[0], sessionAESKey, sessionAESIv)  # encrypt salt for that staff
                sock.send(staffSalt)  # send salt
            elif int(input[0]) == 1:  # receiving login password
                staffInfo = input[1]
                staffName = staffInfo[0]
                encryptedStaffPassword = staffInfo[1]
                staffPassword = decryptAES(encryptedStaffPassword.encode(), sessionAESKey, sessionAESIv)  # decrypt hashed password
                mes = json.dumps([str(3), staffName])
                if len(servers) != 0:
                    check = loginCheck(servers, 12002, mes)  # check if staffmember is already online somewhere
                else:
                    check = 1  # if there is only one server the staff can't be online on another one
                if staffName in staffOnline:  # staff is already online on this server
                    print('Staffmember is already online on this server')
                    answ = 2
                elif int(check) == 0:  # staff is already online on another server
                    print('Staffmember is already online on another server')
                    answ = 4
                elif not staffName in staffPasswords:  # staff doesn't exist
                    print('Staffmember does not exist')
                    answ = 3
                elif staffPassword.encode() == staffPasswords[staffName][1]:  # Staff is allowed to log in
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
                roomsToClean.append(addRoom)
                print("Added room " + str(addRoom))
                sock.send(json.dumps([str(21)]).encode())
                staffOnline.pop(staffName)
    except ConnectionResetError:  # when staff closes program, they log out
        print(staffName + " has closed connection")
        robotsOnline.pop(staffName)  # remove staff from online list
        return

# handles messages coming in from another robot
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
            if not input1:   # sometimes after a connection closes empty messages come through
                break
            input = json.loads(input1)
            if int(input[0]) == 0:  # receiving robotId
                robotId = input[1]
                if robotId not in hashPasswords:
                    mes = 'RobotId does not exist'
                    sock.send(mes.encode())
                    return
                mes = hashPasswords[robotId]
                robotSalt = encryptAES(mes[0], sessionAESKey, sessionAESIv)  # encrypt salt for that robot
                sock.send(robotSalt)  # send salt
            elif int(input[0]) == 1:  # receiving login password
                robotInfo = input[1]
                robotName = robotInfo[0]
                encryptedRobotPassword = robotInfo[1]
                robotPassword = decryptAES(encryptedRobotPassword.encode(), sessionAESKey, sessionAESIv)  # decrypt hashed password
                mes = json.dumps([str(3), robotId])
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
                elif not robotId in hashPasswords:  # Robot doesn't exist
                    print('Robot id does not exist')
                    answ = 3
                elif robotPassword.encode() == hashPasswords[robotId][1]:  # Robot is allowed to log in
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
                    done = False
                    while done == False:
                        roomMutex.acquire()
                        try:
                            if len(roomsToClean) != 0:
                                print("Rooms currently needing cleaning: " + str(len(roomsToClean)))
                                newRoom = roomsToClean.pop(0)
                                answer = json.dumps([11, newRoom])
                                print("Sending robot to " + str(newRoom))
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
roomsToClean = [5, 20, 32]
robotsOnline = {}  # Robots currently online
staffOnline = {}
# dictionary containing robots for testing, salt + hashed password
hashPasswords = {'1': (b'$2b$14$y1.Hk0K5ZlOddaVF1oWP6.', b'$2b$14$y1.Hk0K5ZlOddaVF1oWP6.NPRLt8YPfDHeOa2DkmU63E1Wvii5FOy'),
                 '2': (b'$2b$14$ZmesmMUmDrSdaFLWpMf6Fe', b'$2b$14$ZmesmMUmDrSdaFLWpMf6FeWmuF3eB/WBFxC6HUKTvgfdfaGWWBOBe'),
                 '3': (b'$2b$14$IVxGsAYb8ycDW1JnTyDTuO', b'$2b$14$IVxGsAYb8ycDW1JnTyDTuOUjyIFwgttZeGafTGV6i1Gj3qo41VXE6'),
                 '4': (b'$2b$14$/Dq6GdyDWR9CrYzkrbnUW.', b'$2b$14$/Dq6GdyDWR9CrYzkrbnUW.qAFqSuvcubQq/MXn1sJgMhfn8h29OLW')}
# dictionary containing staff for testing, salt + hashed password
staffPasswords = {'Gwen': (b'$2b$14$getcgbCfJbfBPe5BgRrcGO', b'$2b$14$getcgbCfJbfBPe5BgRrcGOf/LhvnalJ6GkUa5ZJL8Z3OtZQ1wBCPq'),
                 'Nico': (b'$2b$14$xE0hfDYcUE5B0y2YCIOhue', b'$2b$14$xE0hfDYcUE5B0y2YCIOhueSi1m9Zbv8lvwHMGuePh0xk6zJxPkHBK'),
                 'Amiel': (b'$2b$14$iQeWFL/oIeJw8nxcsMDPO.', b'$2b$14$iQeWFL/oIeJw8nxcsMDPO.JOKaKE9MTx9pz9mmfi9cSyLWXESQRBW'),
                 'Bellard': (b'$2b$14$21KgNRRVsCG8yHwmeerP5u', b'$2b$14$21KgNRRVsCG8yHwmeerP5uraOPoJBU5wQ03UuHsaco6.zaBwARy4O')}
servers = []  # Servers connected to the network
servNum = raw_input("Enter number of servers you want to link: ")
if int(servNum) != 0:
    for x in range(1, int(servNum)+1):
        servIp = raw_input("Enter IP address for server number " + str(x) + ": ")
        servers.append(servIp)
print("Other servers in network: " + str(len(servers)))
serverSocket = openSock()  # Socket to communicate with robots
syncSocket = openServerSock()  # Socket to communicate with other servers
staffSocket  = openStaffSock()
roomMutex = Lock()
thread1 = RobotThread(listenNewConnection, serverSocket)  # Thread listening to new robots
thread1.start()
thread2 = ServerThread(listenToNewServer, syncSocket)  # Thread listening to other servers
thread2.start()
thread3 = StaffThread(listenToNewStaff, staffSocket)  # Thread listening to other servers
thread3.start()
