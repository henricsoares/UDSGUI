mpMessage = [
    [.0002, -3.2768, -3.2768, 3.2766],  # Sensor horizont. angle
    [.0002, -1.6384, -1.6384, 1.6382],  # Sensor verical. angle
    [.001, -32, -32, 31.999],  # Vehicle coordinate system x-y-z, Sensor x-y-z-coordinate  # noqa: E501
    [.01, 0, .01, 10.23]  # Ground
]


def calcData(data, info):
    if info[2] <= data <= info[3]:
        data = (int((data - (-info[1])) / info[0]))
        data = data.to_bytes(2, 'big', signed=True)
        print('ok')
    else:
        data = 0
        print("Out of range")
    return data


data = calcData(15, mpMessage[2])
print(data)
