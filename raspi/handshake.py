import serial


def perform_handshake(ser):
    wait_for_begin()
    sync_acks()
    print "Done"


def wait_for_begin(ser):
    while True:
        data = ser.readline().strip()
        if data == 'BEGIN':
            return


def sync_acks(ser):
    while True:
        ser.write('ACK')
        data = ser.readline().strip()
        if data == 'ACK':
            return
