''''import random
tx = (b'\x22\xFD\x12')

seed = ["{:08b}".format(random.getrandbits(2)) for _ in range(4)]
binSeed = ''.join(str(e) for e in seed)

rx = (b'\xFD\x12\x01\x01')[2:].hex()

read = b'\x22' '''

'''service = read + bytes.fromhex(input('service: ')) +\
                    bytes.fromhex(input('service: '))
print(service, service.hex())'''
# print('1010'.hex())
chave = 'fa98f388a628a2409e5892a096889a7000c8'
msg = bytes.fromhex(chave)
print(msg.hex() == chave)
