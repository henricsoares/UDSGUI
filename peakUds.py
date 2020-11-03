from uds import Uds

E400 = Uds(resId=0x600, reqId=0x650,
           transportProtocol='CAN',
           interface='peak',
           device='PCAN_USBBUS1',
           baudrate='500000')

try:
    response = E400.send([0x22, 0xF1, 0x8C])  # gets the entire response from the ECU  # noqa: E501
except Exception:
    print('Send did not complete')

if(response[0] == 0x7F):
    print('Negative response')
else:
    serialNumberArray = response[3:]  # cuts the response down to just the serial number serialNumberString = “” # initialises the string for i in serialNumberArray: serialNumberString += chr(i) # Iterates over each element and converts the array element into an ASCII string print(serialNumberString) # prints the ASCII string  # noqa: E501
    print(serialNumberArray)
