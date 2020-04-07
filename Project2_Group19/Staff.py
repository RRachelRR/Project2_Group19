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
from nacl.public import PrivateKey, Box     # elliptic curve algorithm using Ed25519 curve
from nacl.encoding import Base64Encoder
import sys

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
# Socket Stuff
broadcastSocket = socket(AF_INET, SOCK_DGRAM)
broadcastSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
broadcastSocket.settimeout(3)
broadcastSocket.bind(('', 8888))
print("Listening for server broadcast")
while True:
    try:
        data = broadcastSocket.recv(1024)
        break
    except Exception as e:
        if e ==-1007:
            pass

broadcastSocket.close()
data = data.decode('utf-8')
delim = data.split(", ")

staffName = raw_input("Staff Username: ")
staffPassword = raw_input("Password: ")
print("Please wait till you are logged in, this can take a while due to encryption")
try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((delim[0], int(delim[2])))
except ConnectionRefusedError:
    print('Humorous Server Offline Message that no one thinks is funny')
    loginSuccessful = False

if loginSuccessful:
    # Generate ECC Keys
    privateKeyECC = PrivateKey.generate()
    publicKeyExport = privateKeyECC.public_key.encode()

    # Send public key to server
    clientSocket.send(publicKeyExport)  # Send public key to server

    # Receive server's public key
    serverPublicKey = clientSocket.recv(256)
    decodedServerKey = nacl.public.PublicKey(serverPublicKey)

    cipherObjectECC = Box(privateKeyECC, decodedServerKey)  # Object to encrypt and decrypt with key

    # Receive AES key and iv from server
    encryptedKey = clientSocket.recv(1024)
    encryptedIv = clientSocket.recv(1024)
    key = cipherObjectECC.decrypt(encryptedKey)  # decrypts key
    iv = cipherObjectECC.decrypt(encryptedIv)  # decrypts iv

    message = json.dumps([str(0), staffName])
    clientSocket.send(message.encode())
    incom = clientSocket.recv(1024)
    if incom.decode() == 'Username does not exist':
        print(incom.decode())
        active = False
    else:
        robotSalt = decryptAES(incom)
        hashedAndSalted = bcrypt.hashpw(staffPassword.encode(), robotSalt.encode())
        encryptedHash = encryptAES(hashedAndSalted)
        try:
            message = json.dumps([str(1), [staffName, encryptedHash.decode()]])
            clientSocket.send(message.encode())
            login = json.loads(clientSocket.recv(1024).decode())
            
            if int(login[0]) == 1:
                print('Welcome to the Hospital System')
                active = True
            elif int(login[0]) == 2:
                print('Staffmember is already logged in')
            elif int(login[0]) == 3:
                print('Staffmember does not exist')
            elif int(login[0]) == 4:
                print('Staffmember is already logged in on another server')
            else:
                print('Wrong name or password')
        except ConnectionResetError:
            print('Humorous Server Connection Error Message that nobody thinks is funny')
            active = False
        except ConnectionRefusedError:
            print('Humorous Server Offline Message that nobody thinks is funny')
            active = False



if active:
    room = raw_input("Room that needs cleaning: ")
    message1 = json.dumps([2, room])
    try:
        clientSocket.send(message1.encode())
        status = json.loads(clientSocket.recv(1024).decode())
        if int(status[0]) == 21:
            print("Room " + room + " added successfully")
        else:
            print("Adding room was unsuccessful") # This is an error message and should never be displayed
            # if this is reached, something is wrong
    except ConnectionResetError:
        print('Humorous Server Error Message that no ond thinks is funny')
    clientSocket.close()


