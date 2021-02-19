from uds import Uds  # noqa: F401
from time import sleep  # noqa: F401
# sgu
'''a = Uds(reqId=0x757, resId=0x7C1, interface='peak',
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
print('Serial Number response: ' + str(sNResponse))'''
a = Uds(reqId=0x18DA2AF1, resId=0x18DAFA2A, interface='peak',
        device="PCAN_USBBUS1", baudrate='500000')
print(a)

try:
    sn = a.send([0x02, 0x3E, 0x00])
    print(sn)
except Exception as e:
    print(e)
