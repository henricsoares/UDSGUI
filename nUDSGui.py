import tkinter as tk
from tkinter import messagebox  # noqa: F401
from uds import Uds  # noqa: F401
import string  # noqa: F401
from time import time
from threading import Thread
import tkinter.scrolledtext as tkst
from datetime import datetime
from can.interface import Bus  # noqa: F401
from udsoncan.connections import PythonIsoTpConnection  # noqa: F401
from udsoncan.client import Client  # noqa: F401
import isotp  # noqa: F401
from udsoncan import Response  # noqa: F401


class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.winfo_toplevel().title("   UDS on Python")
        master.iconphoto(False, tk.PhotoImage(file='logo.png'))
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.conn = None
        self.client = None
        self.tpTime = 0
        self.tpTimee = 0
# ------ connection title
        self.connectionTitleMenu = tk.Canvas(self.frame, width=600, height=100,
                                             bd=0, highlightthickness=0)
        self.requestTitleLabel = tk.Label(self.connectionTitleMenu,
                                          text='Configure the connection',
                                          relief=tk.RIDGE,
                                          font=('verdana', 10, 'bold'))
        self.requestTitleLabel.pack(pady=15)
        # self.connectionTitleMenu.pack(side=tk.TOP)
        self.connectionTitleMenu.grid(row=0, column=0)
# ------ communication menu
        self.communicationMenu = tk.Canvas(self.frame, width=600, height=100,
                                           bd=0, highlightthickness=0)
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
        self.sensor = tk.StringVar(window)
        self.sensors = ('SGU', 'BEG')
        self.sensor.set(self.sensors[0])
        self.sensorLabel = tk.Label(self.communicationMenu,
                                    text='Sensor:')
        self.sensorOptions = tk.OptionMenu(self.communicationMenu,
                                           self.sensor,
                                           *self.sensors)
        # self.sensorOptions.config(state='disabled')
        self.bdLabel = tk.Label(self.communicationMenu, text='Baudrate:')
        self.baudRate = tk.Entry(self.communicationMenu, bd=5, width=6,
                                 justify='center')
        self.baudRate.insert(0, '500000')
        self.baudRate.config(state='disabled')

        self.reqIdLabel.grid(row=2, column=0)
        self.reqId.grid(row=2, column=1)
        self.resIdLabel.grid(row=2, column=2)
        self.resId.grid(row=2, column=3)
        self.interfaceLabel.grid(row=1, column=0)
        self.interfaceOptions.grid(row=1, column=1)
        self.deviceLabel.grid(row=1, column=2)
        self.deviceOptions.grid(row=1, column=3)
        self.sensorLabel.grid(row=0, column=0)
        self.sensorOptions.grid(row=0, column=1)
        self.bdLabel.grid(row=0, column=2)
        self.baudRate.grid(row=0, column=3)
        # self.communicationMenu.pack(side=tk.TOP)
        self.communicationMenu.grid(row=1, column=0, pady=5)
# ------ comm status
        self.commStatus = False
        self.commButton = tk.Button(self.communicationMenu, text="Connect",
                                    command=self.configComm)
        self.commLabel = tk.Label(self.communicationMenu,
                                  text='Comm status:')
        self.commStatuss = tk.Label(self.communicationMenu,
                                    text=str(self.commStatus))
        self.commLabel.grid(row=3, column=2)
        self.commStatuss.grid(row=3, column=3)
        self.commButton.grid(row=3, column=1)
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
        self.begServices = {
                         'Diagnostic Session Control': 0x10,
                         'ECU Reset': 0x11,
                         'Comunication Control': 0x28,
                         'Tester Present': [0x3E, 0x00],
                         'Read Data': 0x22,
                         'Write Data': 0x2E,
                         'Read DTC Information': 0x19,
                         'Clear Diagnostics Information': 0x14,
                         'Control DTC Setting': 0x85,
                         'Security Access': 0x27}
        self.begDataToRead = {
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
        self.dataToWrite = {
            'Write enable/disable B messages': 0xFD11,
            'Write CAN1 baud rate': 0xFD12,
            'Write CAN1 diagnostics messages IDs': 0xFD14,
            'Write configure object/filtered object message IDs': 0xFD15,
            'Write configure single CAN message ID': 0xFD16,
            'Write configure object/filtered object message prioritization': 0xFD18,  # noqa: E501
            'Write configure number of objects/filtered objects to be sent': 0xFD19,  # noqa: E501
            'Configure antenna modulation combinations': 0xFD26,
            'Configure CAN communication protocol': 0xFD27,
            'Configure mounting position': 0xFD28,
            'Configure zone configuration': 0xFD60,
            'Configure layer': 0xFD61,
            'Configure enable/disable object/filtered object and/or zone message': 0xFD62,  # noqa: E501
            'Configure radar wave emission stop': 0xFD63,
            'Configure output coordinate system': 0xFD64}
        self.dataOptions = {'Read Data': self.begDataToRead,
                            'Write Data': self.dataToWrite}

        self.service = tk.StringVar(window)
        self.service.trace('w', self.updateData)
        self.sensor.trace('w', self.updateIDS)
        self.serviceLabel = tk.Label(self.begRequestMenu, text='SID')
        self.serviceOptions = tk.OptionMenu(self.begRequestMenu, self.service,
                                            *self.begServices.keys())
        # self.serviceOptions.config(state='disabled')
        self.DSCSF = {
                      'Default diagnostic session': 0x01,
                      'Extended diagnostic session': 0x03
                      }
        self.ECUR = {
                     'Hard Reset': 0x01
                     }
        self.RDTCI = {
            'reportDTCByStatusMask': 0x02,
            'reportDTCExtDataRecordByDTCNumber': 0x06}
        self.sfOptions = {
            'Diagnostic Session Control': self.DSCSF,
            'ECU Reset': self.ECUR,
            'Read DTC Information': self.RDTCI}
        self.begTPS = {
            'ON - With response': [0x3e, 0x00],
            'OFF': ''}
        self.begRequestMenu = tk.Canvas(self.frame, width=600, height=400,
                                        bd=0, highlightthickness=0)
        self.begDID = tk.StringVar(self)
        self.begDIDLabel = tk.Label(self.begRequestMenu,
                                    text='Read Data By Identifier: ')
        self.begDIDOptions = tk.OptionMenu(self.begRequestMenu, self.begDID,
                                           *self.begDataToRead.keys())
        self.begTP = tk.StringVar(self)
        self.begTP.set('OFF')
        self.begTP.trace('w', self.startTrd)
        self.begTPLabel = tk.Label(self.begRequestMenu,
                                   text='Tester Present: ')
        self.begTPOptions = tk.OptionMenu(self.begRequestMenu, self.begTP,
                                          *self.begTPS.keys())
        self.begSend = tk.Button(self.begRequestMenu, text="Send",
                                 command=self.sendMsg)
        self.begResponse = tk.Label(self.begRequestMenu,
                                    text='Response: ')
        self.begDIDLabel.grid(row=1, column=0)
        self.begDIDOptions.grid(row=1, column=1)
        self.begSend.grid(row=2, column=0)
        self.begResponse.grid(row=2, column=1)
        self.begTPLabel.grid(row=0, column=0)
        self.begTPOptions.grid(row=0, column=1)
        # self.begRequestMenu.pack(side=tk.TOP)
# ------ request menu for SGU
        self.sguDIDS = {
            'Programming Attempt Counter': b'\x22\xf1\x10',
            'Boot Software Identification': b'\x22\xf1\x80',
            'Application Software Identification': b'\x22\xf1\x81',
            'Active Diagnostic Session': b'\x22\xf1\x86',
            'ECU Voltage': b'\x22\xf1\x87',
            'ECU Software Number': b'\x22\xf1\x88',
            'ECU Manufacturing Date': b'\x22\xf1\x8b',
            'Serial Number': b'\x22\xf1\x8c',
            'ECU Hardware Partnumber': b'\x22\xf1\x91',
            'ECU Hardware Version Information': b'\x22\xf1\x93',
            'ECU Temperature': b'\x22\xf1\x94',
            'SDA Horizontal Misalignment Angle': b'\x22\xfc\x01',
            'SDA Vertical Alignment Angle': b'\x22\xfc\x02',
            'SDA Status': b'\x22\xfc\x03'}
        self.sguTPS = {
            'ON - With response': [0x3e, 0x00],
            'ON - Without response': [0x3e, 0x80],
            'OFF': ''}
        self.sguRequestMenu = tk.Canvas(self.frame, width=600, height=400,
                                        bd=0, highlightthickness=0)
        self.sguDID = tk.StringVar(self)
        self.sguDIDLabel = tk.Label(self.sguRequestMenu,
                                    text='Read Data By Identifier: ')
        self.sguDIDOptions = tk.OptionMenu(self.sguRequestMenu, self.sguDID,
                                           *self.sguDIDS.keys())
        self.sguTP = tk.StringVar(self)
        self.sguTP.set('OFF')
        self.sguTP.trace('w', self.startTrd)
        self.sguTPLabel = tk.Label(self.sguRequestMenu,
                                   text='Tester Present: ')
        self.sguTPOptions = tk.OptionMenu(self.sguRequestMenu, self.sguTP,
                                          *self.sguTPS.keys())
        self.sguSend = tk.Button(self.sguRequestMenu, text="Send",
                                 command=self.sendMsg)
        self.sguResponse = tk.Label(self.sguRequestMenu,
                                    text='Response: ')
        self.sguDIDLabel.grid(row=1, column=0)
        self.sguDIDOptions.grid(row=1, column=1)
        self.sguSend.grid(row=2, column=0)
        self.sguResponse.grid(row=2, column=1)
        self.sguTPLabel.grid(row=0, column=0)
        self.sguTPOptions.grid(row=0, column=1)
        # self.sguRequestMenu.pack(side=tk.TOP)
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

    def updateData(self, *args):
        try:
            if self.service.get() == 'Write Data':
                self.dataRecord.config(state=tk.NORMAL)
            else:
                self.dataRecord.delete(0, tk.END)
                self.dataRecord.config(state=tk.DISABLED)
            menu = self.dIdentifierOptions['menu']
            menu1 = self.sFunctionOptions['menu']
            menu.delete(0, 'end')
            menu1.delete(0, 'end')
            self.dataIdentifier.set('')
            self.sFunction.set('')
            if self.service.get() == 'Write Data' or self.service.get() == 'Read Data':  # noqa: E501
                didOptions = (self.dataOptions.get(self.service.get(), '')).keys()  # noqa: E501
                for option in didOptions:
                    menu.add_command(label=option, command=lambda selected=option: self.dataIdentifier.set(selected))  # noqa: E501
            elif self.service.get() == 'Diagnostic Session Control' or self.service.get() == 'ECU Reset' or self.service.get() == 'Read DTC Information':   # noqa: E501
                sfOptions = (self.sfOptions.get(self.service.get(), '')).keys()
                for option in sfOptions:
                    menu1.add_command(label=option, command=lambda selected=option: self.sFunction.set(selected))  # noqa: E501'''
        except Exception:
            self.dataIdentifier.set('')
            menu = self.dIdentifierOptions['menu']
            menu.delete(0, 'end')
            self.sFunction.set('')
            menu1 = self.sFunctionOptions['menu']
            menu1.delete(0, 'end')

    def updateIDS(self, *args):
        if self.sensor.get() == 'SGU':
            self.reqId.config(state='normal')
            self.resId.config(state='normal')
            self.reqId.delete(0, 'end')
            self.reqId.insert(0, '757')
            self.resId.delete(0, 'end')
            self.resId.insert(0, '7C1')
            self.reqId.config(state='disabled')
            self.resId.config(state='disabled')
        elif self.sensor.get() == 'BEG':
            self.resId.config(state='normal')
            self.reqId.config(state='normal')
            self.reqId.delete(0, 'end')
            self.reqId.insert(0, '18DA2AF1')
            self.resId.delete(0, 'end')
            self.resId.insert(0, '18DAFA2A')
            self.resId.config(state='disabled')
            self.reqId.config(state='disabled')

    def sendRequest(self):
        if self.service.get() == '':
            messagebox.showinfo("Error",
                                'Select a SID')
        else:
            if self.service.get() == 'Read Data':
                if self.dataIdentifier.get() != '':
                    message = (hex(self.begServices.get(self.service.get(),
                                   '')),
                               hex(self.begDataToRead.get(self.dataIdentifier.get(),  # noqa: E501
                                                          '')))
                    if tk.messagebox.askyesno('Confirm', "SID: " + self.service.get() + "\n" + "DID: " + self.dataIdentifier.get()):  # noqa: E501
                        self.response['text'] = 'Request: ' + str(message)
                        # print(message)
                else:
                    messagebox.showinfo("Error",
                                        'DID is missing')

            elif self.service.get() == 'Write Data':
                if self.dataRecord.get() != '' and self.dataIdentifier.get() != '':  # noqa: E501
                    message = (hex(self.begServices.get(self.service.get(),
                               '')),
                               hex(self.dataToWrite.get(self.dataIdentifier.get(),  # noqa: E501
                                                        '')),
                               self.dataRecord.get())

                    if tk.messagebox.askyesno('Confirm the content',
                                              "SID: " + self.service.get() + "\n" + "DID: " + self.dataIdentifier.get() + "\n" + "Data: " + self.dataRecord.get()):  # noqa: E501
                        self.response['text'] = 'Request: ' + str(message)
                        # print(message)
                elif self.dataIdentifier.get() == '':
                    messagebox.showinfo("Error",
                                        'DID is missing')
                elif self.dataRecord.get() == '':
                    messagebox.showinfo("Error",
                                        'Data Record is missing')
            elif self.service.get() == 'Diagnostic Session Control' or self.service.get() == 'ECU Reset' or self.service.get() == 'Read DTC Information':   # noqa: E501
                message = (hex(self.begServices.get(self.service.get(), '')),
                           hex((self.sfOptions.get(self.service.get())).get(self.sFunction.get())))  # noqa: E501
                if tk.messagebox.askyesno('Confirm the content',
                                          "SID: " + self.service.get() + "\n" + "SubFn: " + self.sFunction.get()):  # noqa: E501
                    self.response['text'] = 'Request: ' + str(message)
                # print(hex((self.sfOptions.get(self.service.get())).get(self.sFunction.get())))  # noqa: E501
            else:
                if tk.messagebox.askyesno('Confirm the content',
                                          self.service.get()):
                    # self.response['text'] = 'Request: ' + str(message)
                    msg = self.a.send(self.begServices.get(self.service.get()))
                    '''if msg[0] == 0x7e:
                        msg[1] = 'Positive response '
                    else:
                        msg[1] = 'Negative response '''
                    self.response['text'] = 'Response: ' + str(msg)

    def configComm(self):
        if not self.commStatus:
            aux = True
            msg = ''
            if self.sensor.get() != 'SGU' and self.sensor.get() != 'BEG':
                '''reqId, resId = self.reqId.get(), self.resId.get()
                interface, device = self.interface.get(), self.device.get()
                baudrate = self.baudRate.get()
                if not all(c in string.hexdigits for c in reqId) or\
                   reqId == '':
                    msg = 'Invalid redId'
                    aux = False
                else:
                    reqId = int(reqId, 16)
                if not all(c in string.hexdigits for c in resId) or\
                   resId == '':
                    msg = 'Invalid resId'
                    aux = False
                else:
                    resId = int(resId, 16)
                if interface not in self.interfaces or interface == '':
                    msg = 'Invalid interface'
                    aux = False
                if device not in self.devices or device == '':
                    msg = 'Invalid device'
                    aux = False
                if not all(c in string.digits for c in baudrate) or\
                   baudrate == '':
                    msg = 'Invalid baudrate'
                    aux = False'''
                aux = False
                msg = "Device not supported."
            if aux:
                try:
                    if self.sensor.get() == 'SGU':
                        tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits,  # noqa: E501
                                                txid=0x757,
                                                rxid=0x7C1)
                        bus = Bus(bustype='pcan',
                                  channel='PCAN_USBBUS1',
                                  bitrate=500000)
                        stack = isotp.CanStack(bus=bus, address=tp_addr)
                        self.conn = PythonIsoTpConnection(stack)
                        self.sguRequestMenu.grid(row=3, column=0, pady=5)
                    elif self.sensor.get() == 'BEG':
                        tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits,  # noqa: E501
                                                txid=0x18DA2AF1,
                                                rxid=0x18DAFA2A)
                        bus = Bus(bustype='pcan',
                                  channel='PCAN_USBBUS1',
                                  bitrate=500000)
                        stack = isotp.CanStack(bus=bus, address=tp_addr)
                        self.conn = PythonIsoTpConnection(stack)
                        self.begRequestMenu.grid(row=3, column=0, pady=5)
                    self.commStatus = True
                    self.commButton.config(text='Disconnect')
                    self.requestTitleMenu.grid(row=2, column=0)
                    self.terminalMenu.grid(row=4, column=0)
                    self.termPrint('connected', 'Info')
                    self.sensorOptions.config(state='disabled')
                except Exception:
                    messagebox.showinfo('Error', 'There is no connection')
                    self.commStatus = False
            else:
                messagebox.showinfo('Error', msg)
        else:
            try:
                self.commButton.config(text='Connect')
                self.requestTitleMenu.grid_forget()
                self.sguRequestMenu.grid_forget()
                self.begRequestMenu.grid_forget()
                self.terminalMenu.grid_forget()
                self.commStatus = False
                self.sensorOptions.config(state='normal')
            except Exception:
                messagebox.showinfo('Error', 'Unable to disconnect')
        self.commStatuss.config(text=str(self.commStatus))

    def sendMsg(self):
        with Client(self.conn, request_timeout=1,
                    config={'exception_on_unexpected_response':
                            False}) as client:
            if self.sensor.get() == 'SGU':
                if self.sguDID.get() != '':
                    msg = self.sguDIDS.get(self.sguDID.get())
                    try:
                        client.send(msg)
                        self.termPrint(msg, 'Request')
                        payload = client.wait_frame(timeout=1)
                        response = Response.from_payload(payload)  # noqa: F841
                        self.termPrint(response, 'Response')
                    except Exception as e:
                        print(e)
                else:
                    messagebox.showinfo('Error', 'No service selected')
            if self.sensor.get() == 'BEG':
                if self.begDID.get() != '':
                    msg = self.begDataToRead.get(self.begDID.get())
                    try:
                        client.send(msg)
                        self.termPrint(msg, 'Request')
                        payload = client.wait_frame(timeout=1)
                        response = Response.from_payload(payload)  # noqa: F841, E501
                        self.termPrint(response, 'Response')
                    except Exception as e:
                        print(e)
                else:
                    messagebox.showinfo('Error', 'No service selected')
        '''try:
            msg = self.a.send(msg)
            self.termPrint(msg)
        except Exception:
            self.termPrint('No response')'''

    def testerPresent(self, *args):
        self.tpTimee += 4
        while self.commStatus and self.sguTP.get() == 'ON - With response' or self.sguTP.get() == 'ON - Without response':  # noqa: E501
            if self.tpTimee - self.tpTime >= 4:
                self.tpTime, self.tpTimee = time(), time()
                msg = self.sguTPS.get(self.sguTP.get())
                self.termPrint(msg)
                try:
                    msg = self.a.send(self.sguTPS.get(self.sguTP.get()))
                    self.termPrint(msg)
                except Exception:
                    self.termPrint('No response')
            else:
                self.tpTimee = time()

    def termPrint(self, msg, action):
        '''if type(info) is list:
            _msg = []
            for inf in info:
                _msg.append(hex(inf))
            info = str(_msg)'''
        now = datetime.now()
        now = now.strftime('%m/%d/%Y, %H:%M:%S')
        if action == 'Request' or action == 'Response':
            msg = msg.hex()
        self.term.config(state=tk.NORMAL)
        self.term.insert('insert',
                         now + ': ' + '\n' + (action) +
                         ' - ' + msg + '\n')
        self.term.see("end")
        self.term.config(state=tk.DISABLED)

    def startTrd(self, *args):
        Thread(target=self.testerPresent, daemon=True).start()


window = tk.Tk()
app = App(window)
app.mainloop()
