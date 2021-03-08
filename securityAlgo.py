import random

seed = [random.getrandbits(1) for _ in range(32)]
seedValue = int(''.join(str(e) for e in seed), 2)
binSeed = "{:032b}".format(seedValue)
bitPos = [
           26,  # A
           2,   # B
           15,  # C
           7,   # D
           30,  # E
           24,  # F
           13]  # G
rotationCycles = int(''.join(str(seed[e]) for e in bitPos[1:5]), 2)
concatenationRule = ''.join(str(seed[e]) for e in bitPos[5:])
direction = seed[bitPos[0]]
intBits = len(binSeed)
secConstant = 0x8BD6952F
rotationResult: int = 0
possibleKeys = {
    '00': lambda seed=seedValue, rores=rotationResult:
        "{:032b}".format(seed | rores),
    '01': lambda seed=seedValue, rores=rotationResult:
        "{:032b}".format(seed & rores),
    '10': lambda seed=seedValue, rores=rotationResult:
        "{:032b}".format(seed ^ rores),
    '11': lambda const=seedValue, rores=rotationResult:
        "{:032b}".format(const | rores)}


def rotl(num, bits):
    bit = num & (1 << (bits-1))
    num <<= 1
    if(bit):
        num |= 1
    num &= (2**bits-1)

    return num


def rotr(num, bits):
    num &= (2**bits-1)
    bit = num & 1
    num >>= 1
    if(bit):
        num |= (1 << (bits-1))

    return num


if direction:
    rotationResult = seedValue
    for _ in range(rotationCycles):
        rotationResult = rotl(rotationResult, intBits)
else:
    rotationResult = seedValue
    for _ in range(rotationCycles):
        rotationResult = rotr(rotationResult, intBits)
calculatedKey = possibleKeys.get(concatenationRule,
                                 lambda x="Invalid Key": print(x))()
print(' Seed: ' + binSeed + "\n",
      'Rotation Cycles: ' + str(rotationCycles) + '\n',
      'Direction: ' + str(direction) + '\n',
      'Concatenation Rule: ' + concatenationRule + '\n',
      'Rotation Result: ' + "{:032b}".format(rotationResult) + '\n',
      'Calculated Key: ' + str(calculatedKey))
