import serial
import time
import datetime
import keyboard
ser = serial.Serial('COM6', 57600, timeout=0.001)
logfile = open("messagelog.txt", "a")
# ser.write(b'\xFF\xFF\x55\x03\x00\x01\x04\xF8\xFF\x55\x06\x03\xCD\xFF\xFF\xFF\xFF\xFF\x55\x02\x03\xCD\xFF\x55\x04')
ser.write(b'\xFF\x55\x02\x00\x03\xFC\xFF\x55\x03\x04\x00\x1E\xDB\xFF\x55\x03\x04\x00\x1C\xDD\xFF\x55\xFF\x55\xFF\x55\xFF\x55')
message = []


# temporary loop, will make it infinite with breaks later
# for k in range(23):
while 1:
    # idle if buffer empty
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
        #print(csum, end=' should be ')
        #print(int(message[-1], 16))

        if csum == int(message[-1], 16):
            mes_ok = True

    if mes_ok:

        # timestamp
        ts_str = str(datetime.datetime.now().time())
        print('[' + ts_str + '  OK ] ', end=' ')

        # message
        for k in message:
            print(k.upper(), end=' ')
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

# empty the buffer
ser.read(100)
logfile.close()
ser.close()


# while 1:
#     time.sleep(0.1)
#     print('.')
#     if keyboard.is_pressed('y'):
#         break
