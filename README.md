# Project 2 Group 19
> Network of cleaning robots to combat Coronavirus

## Contents
- Requirements
- Libraries
- SQL Database Setup
- Test Cases

## Requirements

Python Compiler Version 3.7 which can be installed [here](https://www.python.org/downloads/)

Note: Library incompatibilities with Python 3.8

## Libraries

### Standard libraries used
- socket
- json
- threading
- time
- base64
- random

### [bcrypt](https://pypi.org/project/bcrypt/)

```shell
$ pip install bcrypt
```

### [cryptodome](https://pycryptodome.readthedocs.io/en/latest/src/installation.html)
 
```shell
$ pip install pycryptodome
```

### [distlib](https://pypi.org/project/distlib/)

```shell
$ pip install distlib
```

### [nacl.utils](https://pypi.org/project/PyNaCl/)

```shell
$ pip install PyNaCl
```

### [mysql.connector](https://pypi.org/project/mysql-connector-python/)

```shell
$ pip install mysql-connector-python
```
## SQL Database Setup

### Installing SQL Server

Go to the link below and download the MySQL Community Server: 

```shell
[https://dev.mysql.com/downloads/mysql/]
```

For macOS download the version titled:
```shell
macOS 10.15 (x86, 64-bit), DMG Archive
```
For Windows, download the version titled:
```shell
Windows (x86, 64-bit), ZIP Archive
```

### Installing SQLWorkbench

Download the SQLWorkbench from the following link:

```shell
[https://www.mysql.com/products/workbench/]
```

Click the "Download Now" button, then navigate to the botton of the page. Select your operating system and click download.

### Start the server

1. Navigate to System Preferences on your device. 
2. Click the MySQL icon. 
3. CLick *initialise database*.
4. Enter a password for the database root user (password123)
5. Click *Use Legacy Password Encryption* and press ok
6. Click *Start MySQL Server*


### Setup a new connection

Open the MySQL Workbench:
1. Click '+' icon beside MySQL Connections
2. Name the connection "Test Connection"
3. Beside password, click *Store in Keychain* and enter password123
4. Click *Test Connection* to check the connection


### Import Database from sqldump file

1. From the bar at the top of the application, select Server > Data Import
2. Choose *Import from Self-Contained File* and select the ``sql_dump.sql`` file
3. Click *Start Import* in the bottom right of the screen

## Test Cases

### Test Case 1
1. Run HospitalServer.py
2. Run Staff.py
3. Enter username: Gwen and password: gwenpw
4. Enter a room number for cleaning

Result: 
- "Welcome to the Hospital System" message displayed after successfull login
- "Room number added successfully" message displayed after room added to cleaning list
- "New Server connection" message displayed in HospitalServer.py 

### Test Case 2
1. Run Robot.py
2. Enter Robot id: 1 and password: robot1

Result:
- "Welcome to the Hospital System" message displayed after successfull login
- Update messages on the current status of the robot outputted periodically
- "New Robot connection" message displayed in HospitalServer.py

### Test Case 3
1. Run Staff.py or Robot.py
2. Enter an incorrect username of password

Result:
- Incorrect username/password messages are diplayed

### Test Case 4
1. Login the same staff/robot at the same time

Result:
- "Staff/robot already logged in" message is displayed

### Test Case 5
1. Run Staff.py or Robot.py without running HospitalServer.py

Result:
- "Server Offline" message is displayed













