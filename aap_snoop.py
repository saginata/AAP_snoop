import serial
import time
import datetime
import keyboard
ser = serial.Serial('COM6', 57600, timeout=0.001)
ser.write(b'\xFF\xFF\x55\x00\x03\xAD\xFF\x55\x04\x03\xCD\xFF\xFF\xFF\xFF\xFF\x55\x04\x03\xCD\xFF\x55\x04')
message = []

# temporary loop, will make it infinite with breaks later
for k in range(23):
    # idle if buffer empty
    while ser.in_waiting == 0:
        time.sleep(0.001)
    # read one byte of the message
    rx = ser.read().hex()
    message.append(rx)

    # detect header of next message
    if len(message) >= 2 and message[-2] == 'ff' and message[-1] == '55':

        # remove it from the current message
        message = message[:-2]

        # print message if not blank (should only be a problem at start)
        if len(message) > 0:

            # timestamp
            ts_str = str(datetime.datetime.now().time())
            print('[' + ts_str + '] ', end=' ')

            # message
            for k in message:
                print(k.upper(), end=' ')
            print('')

        # put the header at the beginning of next message
        message = []
        message.append('ff')
        message.append('55')

# empty the buffer
ser.read(100)
ser.close()


# while 1:
#     time.sleep(0.1)
#     print('.')
#     if keyboard.is_pressed('y'):
#         break
