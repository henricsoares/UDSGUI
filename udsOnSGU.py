from uds import Uds

if __name__ == "__main__":

    a = Uds(reqId=0x757, resId=0x7C1, interface='peak',
            device="PCAN_USBBUS1", baudrate='500000')
    print(a)
    TesterPresent = a.send([0x14, 0x00])
    print('Tester Present request: [0x3E, 0x00]')
    tPResponse = []
    for _hex in TesterPresent:
        tPResponse.append(hex(_hex))
    print('Tester Present response: ' + str(tPResponse))
    SerialNumber = a.send([0x22, 0xF1, 0x94])
    print(SerialNumber)
    print('Serial Number request: [0x22, 0xF1, 0x81]')
    sNResponse = []
    for _hex in SerialNumber:
        sNResponse.append(hex(_hex))
    print('Serial Number response: ' + str(sNResponse))
