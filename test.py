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
'''pnum = (31383).to_bytes(3, 'big', signed=True)
print(int(pnum, 16))
pnum = bytearray(pnum)
print(len(pnum))
pnum = pnum[1:]
print(pnum)
print(type(pnum))
a = b'\x00'
a = a + pnum
print(a.hex())'''
