import tkinter as tk
from tkinter import messagebox  # noqa: F401
import string  # noqa: F401
from time import time, sleep  # noqa: F401
from threading import Thread  # noqa: F401
import tkinter.scrolledtext as tkst
from datetime import datetime
from can.interface import Bus  # noqa: F401
from udsoncan.connections import PythonIsoTpConnection  # noqa: F401
from udsoncan.client import Client  # noqa: F401
import isotp  # noqa: F401
from udsoncan import Response  # noqa: F401
import securityAlgo as sec


class App(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.winfo_toplevel().title("   BEG Config Tool")
        master.iconphoto(False, tk.PhotoImage(file='logo.png'))
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.conn = None
        self.client = None
        self.tpTime = 0
        self.mpMessage = [  # mounting position message info
            [.0002, -3.2768, -3.2768, 3.2766],  # Sensor horizont. angle
            [.0002, -1.6384, -1.6384, 1.6382],  # Sensor verical. angle
            [.001, -32, -32, 31.999],  # Vehicle coordinate system x-y-z, Sensor x-y-z-coordinate  # noqa: E501
            [.01, 0, .01, 10.23]  # Ground
        ]
# ------ connection title
        self.connectionTitleMenu = tk.Canvas(self.frame, width=600, height=100,
                                             bd=0, highlightthickness=0)
        self.requestTitleLabel = tk.Label(self.connectionTitleMenu,
                                          text='Connection',
                                          relief=tk.RIDGE,
                                          font=('verdana', 10, 'bold'))
        self.requestTitleLabel.pack(pady=15)
        self.connectionTitleMenu.grid(row=0, column=0)
# ------ communication menu
        self.communicationMenu = tk.Canvas(self.frame, width=600, height=100,
                                           bd=0, highlightthickness=0)
        self.sensor = tk.StringVar(window)
        self.sensors = ('SGU', 'BEG')
        self.sensor.set(self.sensors[1])
        self.sensorLabel = tk.Label(self.communicationMenu,
                                    text='Sensor:')
        self.sensorOptions = tk.OptionMenu(self.communicationMenu,
                                           self.sensor,
                                           *self.sensors)
        self.sensorOptions.config(state='disabled')
        self.confg = tk.StringVar(window)
        self.confgs = ('Default', 'Custom')
        self.confg.set(self.confgs[0])
        self.confgLabel = tk.Label(self.communicationMenu,
                                   text='Config:')
        self.confgOptions = tk.OptionMenu(self.communicationMenu,
                                          self.confg,
                                          *self.confgs)
        self.confgOptions.config(state='disabled')
        self.sensorLabel.grid(row=0, column=0)
        self.sensorOptions.grid(row=0, column=1)
        self.confgLabel.grid(row=0, column=2)
        self.confgOptions.grid(row=0, column=3)
        self.communicationMenu.grid(row=1, column=0, pady=5, padx=5)
# ------ setup menu - disabled
        self.reqIdLabel = tk.Label(self.communicationMenu, text='Request ID:')
        self.reqId = tk.Entry(self.communicationMenu, bd=5, width=10,
                              justify='center')
        self.reqId.insert(0, '757')
        self.reqId.config(state='disabled')
        self.resIdLabel = tk.Label(self.communicationMenu, text='Response ID:')
        self.resId = tk.Entry(self.communicationMenu, bd=5, width=10,
                              justify='center')
        self.resId.insert(0, '7C1')
        self.resId.config(state='disabled')
        self.interface = tk.StringVar(window)
        self.interfaces = ('peak',)
        self.interface.set(self.interfaces[0])
        self.interfaceLabel = tk.Label(self.communicationMenu,
                                       text='Interface:')
        self.interfaceOptions = tk.OptionMenu(self.communicationMenu,
                                              self.interface,
                                              self.interfaces[0])
        self.interfaceOptions.config(state='disabled')
        self.device = tk.StringVar(window)
        self.devices = ('PCAN_USBBUS1',)
        self.device.set(self.devices[0])
        self.deviceLabel = tk.Label(self.communicationMenu,
                                    text='Device:')
        self.deviceOptions = tk.OptionMenu(self.communicationMenu,
                                           self.device,
                                           self.devices[0])
        self.deviceOptions.config(state='disabled')
        self.bdLabel = tk.Label(self.communicationMenu, text='Baudrate:')
        self.baudRate = tk.Entry(self.communicationMenu, bd=5, width=8,
                                 justify='center')
        self.baudRate.insert(0, '500')
        self.baudRate.config(state='disabled')
        '''self.reqIdLabel.grid(row=2, column=0)
        self.reqId.grid(row=2, column=1)
        self.resIdLabel.grid(row=2, column=2)
        self.resId.grid(row=2, column=3)
        self.interfaceLabel.grid(row=1, column=0)
        self.interfaceOptions.grid(row=1, column=1)
        self.deviceLabel.grid(row=1, column=2)
        self.deviceOptions.grid(row=1, column=3)
        self.bdLabel.grid(row=0, column=2)
        self.baudRate.grid(row=0, column=3)'''
# ------ comm status
        self.commStatus = False
        self.commButton = tk.Button(self.communicationMenu, text="Connect",
                                    command=lambda *args,
                                    passed=self.configComm:
                                    self.startThread(passed, *args))

        self.commLabel = tk.Label(self.communicationMenu,
                                  text='Comm status:')
        self.commStatuss = tk.Label(self.communicationMenu,
                                    text=str(self.commStatus))
        self.commLabel.grid(row=3, column=0)
        self.commStatuss.grid(row=3, column=1)
        self.commButton.grid(row=3, column=3)
# ------ request title
        self.requestTitleMenu = tk.Canvas(self.frame, width=600, height=100,
                                          bd=0, highlightthickness=0)
        self.requestTitle = tk.Label(self.requestTitleMenu,
                                     text='Select a service',
                                     relief=tk.RIDGE,
                                     font=('verdana', 10, 'bold'))
        self.requestTitle.pack(side=tk.TOP, pady=15)
        # self.requestTitleMenu.pack(side=tk.TOP)
# ------ request menu for BEG
        self.begRequestMenu = tk.Canvas(self.frame, width=600, height=400,
                                        bd=0, highlightthickness=0)
        self.begServicesList = [
            ['Read Data', b'\x22'],
            ['Write Data', b'\x2E'],
            ['Diagnostic Session Control', b'\x10'],
            ['ECU Reset', b'\x11'],
            ['Comunication Control', b'\x28'],
            ['Tester Present', b'\x3E\x00'],
            ['Read DTC Information', b'\x19'],
            ['Clear Diagnostics Information', b'\x14'],
            ['Control DTC Setting', b'\x85'],
            ['Security Access', b'\x27']]
        self.begRDBIList = {
            'Read active diagnostic session': b'\x22\xF1\x86',
            'Read system supplier identifier': b'\x22\xF1\x8A',
            'Read ECU manufacturing date': b'\x22\xF1\x8B',
            'Read ECU serial number': b'\x22\xF1\x8C',
            'Read supplier ECU hardware number': b'\x22\xF1\x92',
            'Read system supplier ECU HW version number': b'\x22\xF1\x93',
            'Read system supplier ECU software number': b'\x22\xF1\x94',
            'Read ODXFileDataIdentifier': b'\x22\xF1\x9E',
            'Read enable/disable B messages': b'\x22\xFD\x11',
            'Read configured CAN1 baud rate': b'\x22\xFD\x12',
            'Read current CAN1 baud rate': b'\x22\xFD\x13',
            'Read CAN1 diagnostics messages IDs': b'\x22\xFD\x14',
            'Read object/filtered object message IDs': b'\x22\xFD\x15',
            'Read last configured single CAN message ID': b'\x22\xFD\x16',
            'Read radar ECU CAN message Ids': b'\x22\xFD\x17',
            'Read object/filtered object message prioritization':
            b'\x22\xFD\x18',
            'Read configured number of sent objects/filtered objects':
            b'\x22\xFD\x19',
            'Read antenna modulation combinations': b'\x22\xFD\x26',
            'Read CAN communication protocol': b'\x22\xFD\x27',
            'Read mounting position': b'\x22\xFD\x28',
            'Read current number of sent objects/filtered': b'\x22\xFD\x29',
            'Read zone configuration': b'\x22\xFD\x60',
            'Read layer': b'\x22\xFD\x61',
            'Read enable/disable object/filtered object and/or zone message':
            b'\x22\xFD\x62',
            'Read radar wave emission stop': b'\x22\xFD\x63',
            'Read output coordinate system': b'\x22\xFD\x64'}
        self.begWDBIList = {
            'Write enable/disable B messages': b'\x2E\xFD\x11',
            'Write CAN1 baud rate': b'\x2E\xFD\x12',
            'Write CAN1 diagnostics messages IDs': b'\x2E\xFD\x14',
            'Write configure object/filtered object message IDs': b'\x2E\xFD\x15',  # noqa: E501
            'Write configure single CAN message ID': b'\x2E\xFD\x16',
            'Write configure object/filtered object message prioritization': b'\x2E\xFD\x18',  # noqa: E501
            'Write configure number of objects/filtered objects to be sent': b'\x2E\xFD\x19',  # noqa: E501
            'Configure antenna modulation combinations': b'\x2E\xFD\x26',
            'Configure CAN communication protocol': b'\x2E\xFD\x27',
            'Configure mounting position': b'\x2E\xFD\x28',
            'Configure zone configuration': b'\x2E\xFD\x60',
            'Configure layer': b'\x2E\xFD\x61',
            'Configure enable/disable object/filtered object and/or zone message': b'\x2E\xFD\x62',  # noqa: E501
            'Configure radar wave emission stop': b'\x2E\xFD\x63',
            'Configure output coordinate system': b'\x2E\xFD\x64'}
        self.begDTWList = {
            b'\x2E\xFD\x11': {'disable B message': b'\x00',
                              'enable B message': b'\x01'},
            b'\x2E\xFD\x12': {'125 kbaud': b'\x01',
                              '250 kbaud': b'\x02',
                              '500 kbaud': b'\x03',
                              '1 Mbaud': b'\x04'},
            b'\x2E\xFD\x18': {'Processing': b'\x00',
                              'Distance': b'\x01',
                              'Velocity': b'\x02',
                              'RCS': b'\x03',
                              'Positive angle': b'\x04',
                              'Negative angle': b'\x05'},
            b'\x2E\xFD\x26': {'Tx1 antenna with 208/462 MHz bandwidth':
                              b'\x01',
                              'Tx1 antenna with 462 MHz bandwidth': b'\x02',
                              'Tx1 antenna with 740 MHz bandwidth': b'\x03',
                              'Tx2 antenna with 462 MHz bandwidth': b'\x04',
                              'Tx2 antenna with 740 MHz bandwidt': b'\x05'},
            b'\x2E\xFD\x27': {'Automotive CAN': b'\x00',
                              'SAE J1939': b'\x02'},
            b'\x2E\xFD\x61': {'Filtered object layer': b'\x01',
                              'Object layer': b'\x02'},
            b'\x2E\xFD\x62': {'Messages disabled': b'\x00',
                              'Messages enabled': b'\x01'},
            b'\x2E\xFD\x63': {'Radar wave emission enabled': b'\x00',
                              'Radar wave emission disabled': b'\x01'},
            b'\x2E\xFD\x64': {'Sensor coordinate system': b'\x00',
                              'Vehicle coordinate system': b'\x01'},
            b'\x2E\xFD\x14': '',
            b'\x2E\xFD\x15': '',
            b'\x2E\xFD\x16': '',
            b'\x2E\xFD\x19': '',
            b'\x2E\xFD\x28': '',
            b'\x2E\xFD\x60': ''}
        self.dataOptions = {'Read Data': self.begRDBIList,
                            'Write Data': self.begWDBIList}
        self.DSCSF = {
            'Default diagnostic session': 0x01,
            'Extended diagnostic session': 0x03}
        self.ECUR = {
            'Hard Reset': 0x01}
        self.RDTCI = {
            'reportDTCByStatusMask': 0x02,
            'reportDTCExtDataRecordByDTCNumber': 0x06}
        self.sfOptions = {
            'Diagnostic Session Control': self.DSCSF,
            'ECU Reset': self.ECUR,
            'Read DTC Information': self.RDTCI}
        self.begTPS = {
            'ON': b'\x3E\x00',
            'OFF': ''}
        self.begDSCO = {
            'Default': b'\x10\x01',
            'Extended': b'\x10\x03'}
        self.sendBtn = tk.Canvas(self.frame, width=600, height=400,
                                 bd=0, highlightthickness=0)
        self.begService = tk.IntVar(window)
        self.begRDBIs = tk.Radiobutton(self.begRequestMenu,
                                       text="Read Data By Identifier",
                                       command=self.begServices,
                                       variable=self.begService, value=False,
                                       indicatoron=0)
        self.begDID = tk.StringVar(self)
        self.begDID.trace('w', self.begDIDUpdate)
        self.begDIDOptions = tk.OptionMenu(self.begRequestMenu, self.begDID,
                                           *self.begRDBIList.keys())
        self.begDIDOptions.config(width=15)
        self.begWDBIs = tk.Radiobutton(self.begRequestMenu,
                                       text="Write Data By Identifier",
                                       command=self.begServices,
                                       variable=self.begService, value=True,
                                       indicatoron=0)
        self.begDTW = tk.StringVar(self)
        self.begDTWOptions = tk.OptionMenu(self.begRequestMenu, self.begDTW,
                                           '')
        self.begDTWOptions.config(width=15)
        self.begDataEntry = tk.Entry(self.begRequestMenu, bd=5, width=15,
                                     justify='center')
        self.begSend = tk.Button(self.sendBtn, text="Send",
                                 command=lambda *args,
                                 passed=self.sendMsg:
                                 self.startThread(passed, *args))
        self.begResponse = tk.Label(self.begRequestMenu,
                                    text='Response: ')
        self.begRDBIs.grid(row=2, column=0, pady=5)
        self.begWDBIs.grid(row=2, column=1, pady=5)
        self.begDIDOptions.grid(row=3, column=0)
        self.begSend.grid(row=0, column=0)
# ------ response menu
        self.responseMenu = tk.Canvas(self.frame, width=600, height=100,
                                      bd=0, highlightthickness=0)
        self.response = tk.Label(self.responseMenu,
                                 text='Response: ')
        # self.response.pack(side=tk.TOP)
        # self.responseMenu.pack(side=tk.TOP)
# ------ log menu
        self.terminalMenu = tk.Canvas(self.frame, width=100, height=50,
                                      bd=0, highlightthickness=0)
        self.term = tkst.ScrolledText(master=self.terminalMenu, wrap=tk.WORD,
                                      width=40,
                                      height=10)
        self.term.pack()
# ------

    def configComm(self):
        if not self.commStatus:
            if self.sensor.get() != 'BEG':
                messagebox.showinfo('Error', 'Device not supported.')
            else:
                try:
                    tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits,  # noqa: E501
                                            txid=0x18DA2AF1,
                                            rxid=0x18DAFA2A)
                    bus = Bus(bustype='pcan',
                              channel='PCAN_USBBUS1',
                              bitrate=500000)
                    stack = isotp.CanStack(bus=bus, address=tp_addr)
                    self.conn = PythonIsoTpConnection(stack)
                    self.requestTitleMenu.grid(row=3, column=0, pady=5)
                    self.begRequestMenu.grid(row=4, column=0, pady=5)
                    self.sendBtn.grid(row=5, column=0, pady=5)
                    self.commStatus = True
                    self.commButton.config(text='Disconnect')
                    self.terminalMenu.grid(row=6, column=0)
                    self.termPrint('Info - connected')
                    self.sensorOptions.config(state='disabled')
                except Exception:
                    messagebox.showinfo('Error', 'There is no connection')
                    self.commStatus = False
        else:
            try:
                self.commButton.config(text='Connect')
                self.requestTitleMenu.grid_forget()
                self.begRequestMenu.grid_forget()
                self.terminalMenu.grid_forget()
                self.sendBtn.grid_forget()
                self.commStatus = False
            except Exception:
                messagebox.showinfo('Error', 'Unable to disconnect')
        self.commStatuss.config(text=str(self.commStatus))

    def sendMsg(self):
        msg: str
        if self.sensor.get() == 'BEG':
            service = (self.begServicesList[self.begService.get()])
            if service[0] == 'Read Data' and self.begDID.get() != '':
                msg = self.begRDBIList.get(self.begDID.get())
                self.termPrint('Request', msg)
            elif service[0] == 'Write Data' and self.begDID.get() != '':
                did = self.begWDBIList.get(self.begDID.get())
                if self.begDTW.get() != '':
                    dtw = self.begDTWList.get(did)
                    dtw = dtw.get(self.begDTW.get())
                    msg = did + dtw
                    self.termPrint('Request', msg)
                elif self.begDataEntry.get != '':
                    try:
                        dtw = self.begDataEntry.get()
                        msg = did + bytes.fromhex(dtw)
                        self.termPrint('Request', msg)
                    except Exception:
                        messagebox.showinfo(
                            'Error', 'Incorrect data provided.')
                else:
                    messagebox.showinfo('Error', 'Complete the request')
            else:
                messagebox.showinfo('Error', 'Complete the request')
        with Client(self.conn, request_timeout=1,
                    config={'exception_on_unexpected_response':
                            False}) as client:  # noqa: F841

            if self.sensor.get() == 'BEG':
                if self.begDID.get() != '':
                    msg = self.begRDBIList.get(self.begDID.get())
                    try:
                        self.conn.send(msg)
                        self.termPrint('Request', msg)
                        payload = self.conn.wait_frame(timeout=1)
                        response = Response.\
                            from_payload(payload)  # noqa: F841, E501
                        self.termPrint('Response', response.data)
                    except Exception as e:
                        print(e)
                else:
                    messagebox.showinfo('Error', 'No service selected')

    def testerPresent(self, *args):
        try:
            with Client(self.conn, request_timeout=1,
                        config={'exception_on_unexpected_response':
                                False}) as client:  # noqa: F841
                self.conn.send(b'\x10\x03')
                self.termPrint('Request', b'\x10\x03')
                payload = self.conn.wait_frame(timeout=1)
                response = Response.\
                    from_payload(payload)  # noqa: F841, E501
                response = str(response).split('<')
                response = (response[1].split('-'))[0]
                self.termPrint(response)
                self.conn.send(b'\x27\x63')
                self.termPrint('Request', b'\x27\x63')
                payload = self.conn.wait_frame(timeout=1)
                response = Response.from_payload(payload)
                seed = (response.data.hex()[2:])
                sA = sec.securityAlgo(seed, 'series')
                sleep(.1)
                key = b'\x27\x64' + sA.calculatedKey
                response = str(response).split('<')
                response = (response[1].split('-'))[0]
                self.conn.send(key)
                payload = self.conn.wait_frame(timeout=1)
                response = Response.from_payload(payload)
                response = str(response).split('<')
                response = (response[1].split('-'))[0]
                self.termPrint(response)
            self.tpTime += 4
            service = (self.begServicesList[self.begService.get()])[0]
            while self.commStatus and service == 'Write Data':
                if time() - self.tpTime >= 4:
                    self.tpTime = time()
                    with Client(self.conn, request_timeout=1,
                                config={'exception_on_unexpected_response':
                                        False}) as client:  # noqa: F841
                        msg = b'\x3E\x00'
                        self.conn.send(msg)
                        self.termPrint('Request', msg)
                        '''payload = self.conn.wait_frame(timeout=1)
                        response = Response.\
                            from_payload(payload)  # noqa: F841, E501
                        self.termPrint('Response', response.data)'''
                service = (self.begServicesList[self.begService.get()])[0]
            self.begService.set(0)
        except Exception as e:
            messagebox.showinfo('Function unavailable', e)
            self.begService.set(0)

    def startThread(self, func):
        Thread(target=func).start()

    def termPrint(self, action, msg=''):
        now = datetime.now()
        now = now.strftime('%m/%d/%Y, %H:%M:%S')
        self.term.config(state=tk.NORMAL)
        if action == 'Request' or action == 'Response':
            msg = msg.hex()
            self.term.insert('insert',
                             now + ': ' + '\n' + (action) +
                             ' - ' + msg + '\n')
        else:
            self.term.insert('insert',
                             now + ': ' + '\n' + (action) + '\n')
        self.term.see("end")
        self.term.config(state=tk.DISABLED)

    def begServices(self):
        service = (self.begServicesList[self.begService.get()])
        if service[0] == 'Read Data':
            self.begDTWOptions.grid_forget()
            self.begDataEntry.grid_forget()
            options = self.begRDBIList.keys()
            self.begDID.set('')
            menu = self.begDIDOptions['menu']
            menu.delete(0, 'end')
            for option in options:
                menu.add_command(label=option,
                                 command=lambda selected=option:
                                 self.begDID.set(selected))
        elif service[0] == 'Write Data':
            Thread(target=self.testerPresent, daemon=True).start()
            options = self.begWDBIList.keys()
            self.begDID.set('')
            menu = self.begDIDOptions['menu']
            menu.delete(0, 'end')
            for option in options:
                menu.add_command(label=option,
                                 command=lambda selected=option:
                                 self.begDID.set(selected))

    def begDIDUpdate(self, *args):
        service = (self.begServicesList[self.begService.get()])
        if service[0] == 'Write Data':
            dtw = self.begWDBIList.get(self.begDID.get(), '')
            begdid = (self.begDID.get())
            if begdid == 'Configure mounting position':
                self.mountingWindow()
            else:
                self.begDataEntry.config(state='normal')
            if self.begDTWList.get(dtw, '') != '':
                self.begDataEntry.grid_forget()
                self.begDataEntry.delete(0, "end")
                self.begDTWOptions.grid(row=3, column=1)
                options = self.begDTWList.get(dtw, '')
                self.begDTW.set('')
                menu = self.begDTWOptions['menu']
                menu.delete(0, 'end')
                for option in options:
                    menu.add_command(label=option,
                                     command=lambda selected=option:
                                     self.begDTW.set(selected))
            elif dtw != '':
                self.begDTWOptions.grid_forget()
                self.begDataEntry.grid(row=3, column=1)
                self.begDataEntry.delete(0, "end")
                self.begDTW.set('')

    def mountingWindow(self):
        self.newWindow = tk.Toplevel(self.master)

        self.newWindow.iconphoto(False, tk.PhotoImage(file='logo.png'))
        self.newWindow.title('Mounting Position')

        title = tk.Canvas(self.newWindow)
        tk.Label(title,
                 text="Mounting Position",
                 relief=tk.RIDGE,
                 font=('verdana', 10, 'bold')).pack(pady=15)
        title.grid(row=0, column=0)
        entrys = tk.Canvas(self.newWindow)

        sensorHAngle = tk.Label(entrys, text='Sensor horizont. angle:')
        self.shaId = tk.Entry(entrys, bd=5, width=10,
                              justify='center')
        sensorVAngle = tk.Label(entrys, text='Sensor vertical angle:')
        self.svaId = tk.Entry(entrys, bd=5, width=10,
                              justify='center')

        vehicleCSX = tk.Label(entrys, text='Vehicle coordinate system x:')
        self.vcsxId = tk.Entry(entrys, bd=5, width=10,
                               justify='center')
        vehicleCSY = tk.Label(entrys, text='Vehicle coordinate system y:')
        self.vcsyId = tk.Entry(entrys, bd=5, width=10,
                               justify='center')
        vehicleCSZ = tk.Label(entrys, text='Vehicle coordinate system z:')
        self.vcszId = tk.Entry(entrys, bd=5, width=10,
                               justify='center')

        sensorXC = tk.Label(entrys, text='Sensor x-coordinate:')
        self.sxcId = tk.Entry(entrys, bd=5, width=10,
                              justify='center')
        sensorYC = tk.Label(entrys, text='Sensor y-coordinate:')
        self.sycId = tk.Entry(entrys, bd=5, width=10,
                              justify='center')
        sensorZC = tk.Label(entrys, text='Sensor z-coordinate:')
        self.szcId = tk.Entry(entrys, bd=5, width=10,
                              justify='center')

        ground = tk.Label(entrys, text='Ground:')
        self.gId = tk.Entry(entrys, bd=5, width=10,
                            justify='center')

        sensorHAngle.grid(row=0, column=0, pady=1, padx=1)
        self.shaId.grid(row=0, column=1)
        sensorVAngle.grid(row=1, column=0, pady=1, padx=1)
        self.svaId.grid(row=1, column=1)

        vehicleCSX.grid(row=2, column=0, pady=1, padx=1), self.vcsxId.grid(row=2, column=1)  # noqa: E501
        vehicleCSY.grid(row=3, column=0, pady=1, padx=1), self.vcsyId.grid(row=3, column=1)  # noqa: E501
        vehicleCSZ.grid(row=4, column=0, pady=1, padx=1), self.vcszId.grid(row=4, column=1)  # noqa: E501

        sensorXC.grid(row=5, column=0, pady=1, padx=1), self.sxcId.grid(row=5, column=1)  # noqa: E501
        sensorYC.grid(row=6, column=0, pady=1, padx=1), self.sycId.grid(row=6, column=1)  # noqa: E501
        sensorZC.grid(row=7, column=0, pady=1, padx=1), self.szcId.grid(row=7, column=1)  # noqa: E501

        ground.grid(row=8, column=0, pady=1, padx=1), self.gId.grid(row=8, column=1)  # noqa: E501

        entrys.grid(row=1, column=0)

        done = tk.Canvas(self.newWindow)

        tk.Button(done, text="Done", command=self.getValues).pack()
        done.grid(row=2, column=0, pady=15)

    def getValues(self):
        sha, sva = float(self.shaId.get()), float(self.svaId.get())
        vcsx, vcsy, vcsz = float(self.vcsxId.get()), float(self.vcsyId.get()), float(self.vcszId.get())   # noqa: E501
        sxc, syc, szc = float(self.sxcId.get()), float(self.sycId.get()), float(self.szcId.get())  # noqa: E501
        g = float(self.gId.get())
        sha, sva = self.calcData(sha, self.mpMessage[0]), self.calcData(sva, self.mpMessage[1])    # noqa: E501
        vcsx, vcsy, vcsz = self.calcData(vcsx, self.mpMessage[2]), self.calcData(vcsy, self.mpMessage[2]), self.calcData(vcsz, self.mpMessage[2])  # noqa: E501
        sxc, syc, szc = self.calcData(sxc, self.mpMessage[2]), self.calcData(syc, self.mpMessage[2]), self.calcData(szc, self.mpMessage[2])  # noqa: E501
        g = self.calcData(g, self.mpMessage[3])
        if (sha != 0 and sva != 0 and vcsx != 0 and vcsy != 0 and vcsz != 0
                and sxc != 0 and syc != 0 and szc != 0 and g != 0):
            minfo = (sha + sva + vcsx + vcsy + vcsz + sxc + syc + szc + g).hex()    # noqa: E501
            self.begDataEntry.delete(0, 'end')
            self.begDataEntry.insert(0, minfo)
            self.newWindow.destroy()

        else:
            messagebox.showinfo('Error', 'Invalid value(s).')

    def calcData(self, data, info):
        if info[2] <= data <= info[3]:
            data += 0.0001
            data = (int((data - (-info[1])) / info[0]))
            data = data.to_bytes(3, 'big', signed=True)
            data = bytearray(data)
            data = data[1:]
        else:
            data = 0
        return data


window = tk.Tk()
app = App(window)
app.mainloop()
