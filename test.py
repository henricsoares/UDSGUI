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
lista = []
for i in range(31, -1, -1):
    lista.append(i)
print(lista[9], lista[26], lista[11], lista[31], lista[23], lista[1], lista[16])
