import struct


class securityAlgo:
    def __init__(self, seed, type):
        self.seedValue = int(seed, 16)
        self.binSeed = "{:032b}".format(self.seedValue)
        self.bitPos: list
        self.secConstant: int
        if type == 'sample':
            self.bitPos = [
                    5,  # A
                    29,   # B
                    16,  # C
                    24,   # D
                    1,  # E
                    7,  # F
                    18]  # G
            self.secConstant = 0x8BD6952F
        else:
            self.bitPos = [
                    22,  # A
                    5,   # B
                    20,  # C
                    0,   # D
                    8,  # E
                    30,  # F
                    15]  # G
            self.secConstant = 0x6C47D1F5

        self.rotationCycles = int(''.join(str(self.binSeed[e]) for e in self.bitPos[1:5]), 2)  # noqa: E501
        self.concatenationRule = ''.join(str(self.binSeed[e]) for e in self.bitPos[5:])  # noqa: E501
        self.direction = int(self.binSeed[self.bitPos[0]])
        self.intBits = len(self.binSeed)
        # self.secConstant = 0x6C47D1F5
        self.rotationResult = self.seedValue
        if self.direction:
            for _ in range(self.rotationCycles):
                self.rotl()
        else:
            for _ in range(self.rotationCycles):
                self.rotr()
        self.calculatedKey = self.calculateKey()
        self.calculatedKey = struct.pack(">I", self.calculatedKey)

    def calculateKey(self):
        if self.concatenationRule == '00':
            return (self.seedValue | self.rotationResult)
        elif self.concatenationRule == '01':
            return (self.seedValue & self.rotationResult)
        elif self.concatenationRule == '10':
            return (self.seedValue ^ self.rotationResult)
        elif self.concatenationRule == '11':
            return (self.secConstant ^ self.rotationResult)

    def rotl(self):
        bit = self.rotationResult & (1 << (self.intBits-1))
        self.rotationResult <<= 1
        if(bit):
            self.rotationResult |= 1
        self.rotationResult &= (2**self.intBits-1)

    def rotr(self):
        self.rotationResult &= (2**self.intBits-1)
        bit = self.rotationResult & 1
        self.rotationResult >>= 1
        if(bit):
            self.rotationResult |= (1 << (self.intBits-1))

    def steps(self):
        print(' Seed: ' + self.binSeed + "\n",
              'Rotation Cycles: ' + str(self.rotationCycles) + '\n',
              'Direction: ' + str(self.direction) + '\n',
              'Concatenation Rule: ' + self.concatenationRule + '\n',
              'Rotation Result: ' + "{:032b}".format(self.rotationResult) + '\n',  # noqa: E501
              'Calculated Key: ' + str(self.calculatedKey.hex()))


seed = ('fded5e5b')
sA = securityAlgo(seed, 'series')
print(sA.calculatedKey.hex())
