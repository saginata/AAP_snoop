import serial
import time
import datetime
import keyboard
ser = serial.Serial('COM6', 57600, timeout=0.001)
logfile = open("messagelog.txt", "a")
inputfile = open("fromphone.txt", "r")
dbfile = open("CommandDB.csv", "r")
# ser.write(b'\xFF\xFF\x55\x03\x00\x01\x04\xF8\xFF\x55\x06\x03\xCD\xFF\xFF\xFF\xFF\xFF\x55\x02\x03\xCD\xFF\x55\x04')
ser.write(b'\xff\x55\x08\x04\x00\x27\x04\x00\x02\x33\x27\x6d')

commands = []
descriptions = []
translModes = []

while 1:
    templine = dbfile.readline()
    if len(templine) == 0:
        break

    templinelist = templine.split(";")
    commands.append(templinelist[0])
    descriptions.append(templinelist[1])
    translModes.append(templinelist[2][:-1])
message = []


fromfile = False

if fromfile:
    templine = inputfile.readline()
    templinelist = templine.split(" ")
    readTs = float(templinelist[0])
    messagestr = templinelist[1][:-1]
    message = [messagestr[i:i+2] for i in range(0, len(messagestr), 2)]

# temporary loop, will make it infinite with breaks later
# for k in range(23):
while 1:
    # idle if buffer empty
    if not fromfile:
        while ser.in_waiting == 0:
            time.sleep(0.001)
        # read one byte of the message
        rx = ser.read().hex()
        message.append(rx)

    mes_size = 0
    mes_ok = False

    # record the expected size if message long enough to have one
    if len(message) >= 3:
        mes_size = int(message[2], 16)+1

    # if message ended correctly
    if len(message)-3 == mes_size:

        # CSUM
        csum = 0
        for k in message[2:-1]:
            csum = csum + int(k, 16)
        csum = csum % 256
        csum = 256-csum
        # print(csum, end=' should be ')
        # print(int(message[-1], 16))

        if csum == int(message[-1], 16):
            mes_ok = True

    if mes_ok:

        # timestamp
        ts_str = str(datetime.datetime.now().time())
        print('[' + ts_str + '  OK ] ', end=' ')

        # description
        commandToFind = message[3] + message[4]
        if message[3] == "04":
            commandToFind = commandToFind + message[5]
        print(descriptions[commands.index(commandToFind)].ljust(30), end=" ")
        # print(translModes[commands.index(commandToFind)], end=" ")

        # raw
        if translModes[commands.index(commandToFind)] == "0":
            payload = message[6:-1]
            if message[3] == "00":
                payload.insert(0, message[5])
            print("\"" + ''.join(i for i in payload) + "\"", end=' ')

        # number
        if translModes[commands.index(commandToFind)] == "1":
            payload = message[6:-1]
            if message[3] == "00":
                payload.insert(0, message[5])
            print("\"" + ''.join(i for i in payload) + "\"", end=' ')

        # string
        if translModes[commands.index(commandToFind)] == "2":
            payload = message[6:]
            if message[3] == "00":
                payload.insert(0, message[5])

            payloadint = [int(i, 16) for i in payload]
            print("\"" + ''.join(chr(i) for i in payloadint) + "\"", end=' ')

        # rawer
        if translModes[commands.index(commandToFind)] == "3":
            for k in message:
                print(k.upper(), end=' ')

        # timeelapsed
        if translModes[commands.index(commandToFind)] == "4":
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
        message = []

    # if not ended correctly
    elif len(message) >= 2 and message[-2] == 'ff' and message[-1] == '55':
        print("should never be here")  # remove this later
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

    # if reading from file, the broken messages are split out already, so just print them out
    elif fromfile:
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

    templine = inputfile.readline()
    if len(templine) == 0:
        break

    if fromfile:
        templinelist = templine.split(" ")
        readTs = float(templinelist[0])
        messagestr = templinelist[1][:-1]
        message = [messagestr[i:i+2] for i in range(0, len(messagestr), 2)]

# empty the buffer
ser.read(100)
logfile.close()
inputfile.close()
dbfile.close()
ser.close()


# while 1:
#     time.sleep(0.1)
#     print('.')
#     if keyboard.is_pressed('y'):
#         break
