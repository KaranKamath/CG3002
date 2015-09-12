import serial
ser = serial.Serial(‘/dev/ttyAMA0’, 9600, timeout=1)

ser.open()

ser.write("Hello World!")

ser.close()