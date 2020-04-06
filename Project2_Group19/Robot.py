from random import randrange
from socket import*

import bcrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES,PKCS1_OAEP
import base64
import json
import time

from pip._vendor.distlib.compat import raw_input
import nacl.utils
from nacl.public import PrivateKey, Box


active = False  # False: User needs to log in, True: User is logged in
loginSuccessful = True
currentRoom = 0  # id of the room the robot is currently in

# AES parameters
key = ''
iv = ''
modeAES = AES.MODE_CFB  # Cipher Something Mode


# Encrypt and decode are not exactly taken from this link, but were inspired by this code
# https://stackoverflow.com/questions/14179784/python-encrypting-with-pycrypto-aes


def encryptAES(message):
    # If message is not in bytes makes it bytes
    if type(message) is str:
        bytemessage = message.encode()
        message = bytemessage
    encryptObject = AES.new(key, modeAES, iv)  # Object to encrypt
    cipherText = encryptObject.encrypt(message)  # encrypt message
    return base64.b64encode(cipherText)


def decryptAES(ciphertext):
    # If ciphertext is not string makes it a string
    if type(ciphertext) is not str:
        strtext = base64.b64decode(ciphertext)
        ciphertext = strtext
    decryptObject = AES.new(key, modeAES, iv)  # Object to decrypt
    message = decryptObject.decrypt(ciphertext)  # decrypt message
    return message.decode()


# Socket Stuff
serverName = '127.0.0.1'
serverPort = 12000
serverIn = raw_input("Enter IP address of server you want to log in to (enter 0 for localhost): ")
if serverIn != str(0):
    serverName = serverIn

robotId = raw_input("Robot Id: ")
robotPassword = raw_input("Password: ")
print("Please wait till you are logged in, this can take a while due to encryption")

currentRoom = 0;
cleaning = False;
while(True):
    if cleaning is False:
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName, serverPort))
        except ConnectionRefusedError:
            print('Humorous Server Offline Message that no one thinks is funny')
            loginSuccessful = False

        if loginSuccessful:
            # Generate ECC Keys
            privateKeyECC = PrivateKey.generate()  # Generate private key
            publicKeyExport = privateKeyECC.public_key.encode()

            # Send public key to server
            clientSocket.send(publicKeyExport)

            # Receive server's public key
            serverPublicKey = clientSocket.recv(256)
            decodedServerKey = nacl.public.PublicKey(serverPublicKey)

            cipherObjectECC = Box(privateKeyECC, decodedServerKey)  # Object to encrypt and decrypt with key

            # Receive AES key and iv from server
            encryptedKey = clientSocket.recv(200)
            encryptedIv = clientSocket.recv(1024)
            key = cipherObjectECC.decrypt(encryptedKey)  # decrypts key
            iv = cipherObjectECC.decrypt(encryptedIv)  # decrypts iv

            message = json.dumps([str(0), robotId])
            clientSocket.send(message.encode())
            incom = clientSocket.recv(1024)
            if incom.decode() == 'RobotId does not exist':
                print(incom.decode())
                active = False
            else:
                robotSalt = decryptAES(incom)
                hashedAndSalted = bcrypt.hashpw(robotPassword.encode(), robotSalt.encode())
                encryptedHash = encryptAES(hashedAndSalted)
                try:
                    message = json.dumps([str(1), [robotId, encryptedHash.decode()]])
                    clientSocket.send(message.encode())
                    login = json.loads(clientSocket.recv(1024).decode())
                    if int(login[0]) == 1:
                        print('Welcome to the Hospital System')
                        #currentRoom = login[1]
                        active = True
                    elif int(login[0]) == 2:
                        print('Robot Id is already logged in')
                    elif int(login[0]) == 3:
                        print('Robot Id does not exist')
                    elif int(login[0]) == 4:
                        print('Robot Id is already logged in on another server')
                    else:
                        print('Wrong id or password')
                except ConnectionResetError:
                    print('Humorous Server Connection Error Message that nobody thinks is funny')
                    active = False
                except ConnectionRefusedError:
                    print('Humorous Server Offline Message that nobody thinks is funny')
                    active = False
            message1 = json.dumps([2, [robotId, currentRoom]])
            try:
                clientSocket.send(message1.encode())
                status = json.loads(clientSocket.recv(1024).decode())
                if status[0] == 11:
                    currentRoom = status[1]
                    print("Changing room to " + str(currentRoom))
                    cleaning = True
                elif status[0] == 13:
                    print("Staying at base and waiting for new rooms to become available")
                    time.sleep(30)
                else:
                    print("Staying in this room") # This is an error message and should never be displayed
                    # if this is reached, something is wrong
            except ConnectionResetError:
                print('Humorous Server Error Message that no ond thinks is funny')
                active = False
                clientSocket.close()
    else:
        print("Starting cleaning")
        time.sleep(30)
        print("Room " + str(currentRoom) + " is now cleaned")
        currentRoom = 0
        cleaning = False

