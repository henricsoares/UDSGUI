tx = (b'\x22\xFD\x12')

rx = (b'\xFD\x12\x01\x01')[2:].hex()

read = b'\x22'

service = read + bytes.fromhex(input('service: ')) +\
                    bytes.fromhex(input('service: '))
print(service, service.hex())
