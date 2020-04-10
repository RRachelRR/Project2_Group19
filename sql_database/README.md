# SQL Database
> A guide for connecting a python project to an SQL Database


## Installing SQL Server

Go to the link below and download the MySQL Community Server: 

<https://dev.mysql.com/downloads/mysql/>


For macOS download the version titled:
```shell
macOS 10.15 (x86, 64-bit), DMG Archive
```
For Windows, download the version titled:
```shell
Windows (x86, 64-bit), ZIP Archive
```

## Installing SQLWorkbench

Download the SQLWorkbench from the following link:

<https://www.mysql.com/products/workbench/>


Click the "Download Now" button, then navigate to the botton of the page. Select your operating system and click download.

## Start the server

1. Navigate to System Preferences on your device. 
2. Click the MySQL icon. 
3. CLick *initialise database*.
4. Enter a password for the database root user (password123)
5. Click *Use Legacy Password Encryption* and press ok
6. Click *Start MySQL Server*


## Setup a new connection

Open the MySQL Workbench:
1. Click '+' icon beside MySQL Connections
2. Name the connection "Test Connection"
3. Beside password, click *Store in Keychain* and enter password123
4. Click *Test Connection* to check the connection


## Import Database from sqldump file

1. From the bar at the top of the application, select Server > Data Import
2. Choose *Import from Self-Contained File* and select the ``sqldump.sql`` file
3. Click *Start Import* in the bottom right of the screen


## Connecting Python to SQL Server

The python editor PyCharm can be downloaded [here](https://www.jetbrains.com/pycharm/).

Include the connector library:
1. Navigate: PyCharm > Preferences > Project: PythonMySQL > Project Interpreter
2. Click the *+* icon in the bottom left corner.
3. Search *mysql-connector* and click *install package*

For other IDEs, run the following on the command line:

```shell
$ pip install mysql-connector-python
```



