import serial
import time
import datetime


ser = serial.Serial('COM6', 57600, timeout=0.001)

logfile = open("messagelog.txt", "a")
dbfile = open("CommandDB.csv", "r")

# ser.write(b'\xff\x55\x08\x04\x00\x27\x04\x00\x02\x33\x27\x6d')
bytes()
commands = []
descriptions = []
translModes = []
respModes = []
responses = []

playlists = ["Main", "Now Playing", "Test"]
songs = []

songs.append({'Title': 'Piosenka 1', 'Artist': 'Artysta 1',
              'Album': 'Plyta 1', 'Length': 360})
songs.append({'Title': 'Piosenka 2', 'Artist': 'Artysta 2',
              'Album': 'Plyta 2', 'Length': 666})
songs.append({'Title': 'Piosenka 3', 'Artist': 'Artysta 3',
              'Album': 'Plyta 3', 'Length': 420})
songs.append({'Title': 'Piosenka 4', 'Artist': 'Artysta 4',
              'Album': 'Plyta 4', 'Length': 69})


# load command database
while 1:
    templine = dbfile.readline()
    if len(templine) == 0:
        break

    templinelist = templine.split(";")
    commands.append(templinelist[0])
    descriptions.append(templinelist[1])
    translModes.append(templinelist[2])
    respModes.append(templinelist[3])
    responses.append(templinelist[4][:-1])
message = []

while 1:
    mes_size = 0
    mes_ok = False

    while ser.in_waiting == 0:
        time.sleep(0.001)

    # read one byte of the message
    rx = ser.read().hex()
    message.append(rx)

    # record the expected size if message long enough to have one
    if len(message) >= 3:
        mes_size = int(message[2], 16)+1

    # if expected length reached
    if len(message)-3 == mes_size:

        # Checksum
        csum = 0
        for k in message[2:-1]:
            csum = csum + int(k, 16)
        csum = csum % 256
        csum = 256-csum

        if csum == int(message[-1], 16):
            mes_ok = True

    if mes_ok:

        # region print and log
        foundIndex = 0

        # timestamp
        ts_str = str(datetime.datetime.now().time())
        print('[' + ts_str + ']', end=' ')

        # description
        commandToFind = message[3] + message[4]
        if message[3] == "04":
            commandToFind = commandToFind + message[5]
        if commandToFind in commands:
            foundIndex = commands.index(commandToFind)

        print(descriptions[foundIndex].ljust(30), end=" ")
        # print(translModes[commands.index(commandToFind)], end=" ")

        # raw
        if translModes[foundIndex] == "0":
            payload = message[6:-1]
            if message[3] == "00":
                payload.insert(0, message[5])
            print("\"" + ''.join(i for i in payload) + "\"", end=' ')

        # number
        if translModes[foundIndex] == "1":
            payload = message[6:-1]
            if message[3] == "00":
                payload.insert(0, message[5])
            print("\"" + ''.join(i for i in payload) + "\"", end=' ')

        # string
        if translModes[foundIndex] == "2":
            payload = message[6:]
            if message[3] == "00":
                payload.insert(0, message[5])

            payloadint = [int(i, 16) for i in payload]
            print("\"" + ''.join(chr(i) for i in payloadint) + "\"", end=' ')

        # rawer
        if translModes[foundIndex] == "3":
            for k in message:
                print(k.upper(), end=' ')

        # timeelapsed
        if translModes[foundIndex] == "4":
            payload = message[7:-1]
            payloadstr = ''.join(i for i in payload)
            if len(payloadstr) == 8:
                print(int(payloadstr, 16)/1000, end=' ')
            else:
                print("TRANS ERROR\"" + ''.join(i for i in message) + "\"", end=' ')

        print('')

        # logmessage
        # datetime.datetime.fromtimestamp(time.time())
        logfile.write(str(time.time())+" ")
        for k in message:
            logfile.write(k)
        logfile.write("\n")

        # endregion

        # region Respond
        if respModes[foundIndex] == '0':
            print('[' + ts_str + ']', end=' ')
            print("Not responding")
            logfile.write(str(time.time()) + " Not responding\n")
        elif respModes[foundIndex] == '1':
            responseStr = responses[foundIndex]

            print('[' + ts_str + ']', end=' ')
            print("Responding ", end=' ')
            print(responseStr)

            logfile.write(str(time.time()) +
                          " Responding " + responseStr + "\n")

            response = bytes.fromhex(responseStr)
            ser.write(response)

        elif respModes[foundIndex] == '2':
            abc = 1

        # endregion
        message = []

    # if not ended correctly
    elif len(message) >= 2 and message[-2] == 'ff' and message[-1] == '55':

        # remove it from the current message
        message = message[:-2]

        # print message if not blank (should only be a problem at start)
        if len(message) > 0:

            # timestamp
            ts_str = str(datetime.datetime.now().time())
            print('[' + ts_str + ' NOK ] ', end=' ')

            # message
            for k in message:
                print(k.upper(), end=' ')
            print('')

            # logfile
            logfile.write(str(time.time())+" ")
            for k in message:
                logfile.write(k)
            logfile.write("\n")

            message = []

        # put the header at the beginning of next message
        message = []
        message.append('ff')
        message.append('55')
ser.read(100)
ser.close()
logfile.close()
dbfile.close()
