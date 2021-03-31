import tkinter as tk

mpMessage = [
    [.0002, -3.2768, -3.2768, 3.2766],  # Sensor horizont. angle
    [.0002, -1.6384, -1.6384, 1.6382],  # Sensor verical. angle
    [.001, -32, -32, 31.999],  # Vehicle coordinate system x-y-z, Sensor x-y-z-coordinate  # noqa: E501
    [.01, 0, .01, 10.23]  # Ground
]

master = tk.Tk()
newWindow = tk.Toplevel(master)

newWindow.iconphoto(False, tk.PhotoImage(file='logo.png'))
newWindow.title('Mounting Position')

title = tk.Canvas(newWindow)
tk.Label(title,
         text="Mounting Position",
         relief=tk.RIDGE,
         font=('verdana', 10, 'bold')).pack(pady=15)
title.grid(row=0, column=0)
entrys = tk.Canvas(newWindow)

sensorHAngle = tk.Label(entrys, text='Sensor horizont. angle:')
shaId = tk.Entry(entrys, bd=5, width=10,
                 justify='center')
sensorVAngle = tk.Label(entrys, text='Sensor vertical angle:')
svaId = tk.Entry(entrys, bd=5, width=10,
                 justify='center')

vehicleCSX = tk.Label(entrys, text='Vehicle coordinate system x:')
vcsxId = tk.Entry(entrys, bd=5, width=10,
                  justify='center')
vehicleCSY = tk.Label(entrys, text='Vehicle coordinate system y:')
vcsyId = tk.Entry(entrys, bd=5, width=10,
                  justify='center')
vehicleCSZ = tk.Label(entrys, text='Vehicle coordinate system z:')
vcszId = tk.Entry(entrys, bd=5, width=10,
                  justify='center')

sensorXC = tk.Label(entrys, text='Sensor x-coordinate:')
sxcId = tk.Entry(entrys, bd=5, width=10,
                 justify='center')
sensorYC = tk.Label(entrys, text='Sensor y-coordinate:')
sycId = tk.Entry(entrys, bd=5, width=10,
                 justify='center')
sensorZC = tk.Label(entrys, text='Sensor z-coordinate:')
szcId = tk.Entry(entrys, bd=5, width=10,
                 justify='center')

ground = tk.Label(entrys, text='Ground:')
gId = tk.Entry(entrys, bd=5, width=10,
               justify='center')

sensorHAngle.grid(row=0, column=0, pady=1, padx=1)
shaId.grid(row=0, column=1)
sensorVAngle.grid(row=1, column=0, pady=1, padx=1)
svaId.grid(row=1, column=1)

vehicleCSX.grid(row=2, column=0, pady=1, padx=1), vcsxId.grid(row=2, column=1)
vehicleCSY.grid(row=3, column=0, pady=1, padx=1), vcsyId.grid(row=3, column=1)
vehicleCSZ.grid(row=4, column=0, pady=1, padx=1), vcszId.grid(row=4, column=1)

sensorXC.grid(row=5, column=0, pady=1, padx=1), sxcId.grid(row=5, column=1)
sensorYC.grid(row=6, column=0, pady=1, padx=1), sycId.grid(row=6, column=1)
sensorZC.grid(row=7, column=0, pady=1, padx=1), szcId.grid(row=7, column=1)

ground.grid(row=8, column=0, pady=1, padx=1), gId.grid(row=8, column=1)

entrys.grid(row=1, column=0)

done = tk.Canvas(newWindow)


def calcData(data, info):
    if info[2] <= data <= info[3]:
        data = (int((data - info[1]) / info[0]))
        data = data.to_bytes(2, 'big', signed=True)
        print('ok')
    else:
        data = 0
        print("Out of range")
    return data


def getValues():
    sha, sva = float(shaId.get()), float(svaId.get())
    vcsx, vcsy, vcsz = float(vcsxId.get()), float(vcsyId.get()), float(vcszId.get())   # noqa: E501
    sxc, syc, szc = float(sxcId.get()), float(sycId.get()), float(szcId.get())  # noqa: E501
    g = float(gId.get())
    sha, sva = calcData(sha, mpMessage[0]), calcData(sva, mpMessage[1])
    vcsx, vcsy, vcsz = calcData(vcsx, mpMessage[2]), calcData(vcsy, mpMessage[2]), calcData(vcsz, mpMessage[2])  # noqa: E501
    sxc, syc, szc = calcData(sxc, mpMessage[2]), calcData(syc, mpMessage[2]), calcData(szc, mpMessage[2])  # noqa: E501
    g = calcData(g, mpMessage[3])
    minfo = (sha + sva + vcsx + vcsy + vcsz + sxc + syc + szc + g).hex()
    print(minfo)


doneBtn = tk.Button(done, text="Done",
                    command=getValues).pack()
done.grid(row=2, column=0, pady=15)

master.mainloop()
