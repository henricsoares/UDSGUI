import tkinter as tk
from tkinter import messagebox  # noqa: F401
from uds import Uds
import string


class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.winfo_toplevel().title("UDS on Python")
        self.frame = tk.Frame(window, background="white")
        self.frame.pack(fill=tk.BOTH, expand=True)
# ------ connection title
        self.connectionTitleMenu = tk.Canvas(self.frame, width=600, height=100,
                                             background='white',
                                             bd=0, highlightthickness=0)
        self.requestTitleLabel = tk.Label(self.connectionTitleMenu,
                                          text='Configure the connection:')
        self.requestTitleLabel.pack()
        self.connectionTitleMenu.pack(side=tk.TOP)
# ------ communication menu
        self.communicationMenu = tk.Canvas(self.frame, width=600, height=100,
                                           background='white',
                                           bd=0, highlightthickness=0)
        self.reqIdLabel = tk.Label(self.communicationMenu, text='Request ID:')
        self.reqId = tk.Entry(self.communicationMenu, bd=5, width=5)
        self.reqId.insert(0, '757')
        self.reqId.config(state='disabled')
        self.resIdLabel = tk.Label(self.communicationMenu, text='Response ID:')
        self.resId = tk.Entry(self.communicationMenu, bd=5, width=5)
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
        self.baudRate = tk.Entry(self.communicationMenu, bd=5, width=6)
        self.baudRate.insert(0, '500000')
        self.baudRate.config(state='disabled')
        self.reqIdLabel.pack(side=tk.LEFT)
        self.reqId.pack(side=tk.LEFT)
        self.resIdLabel.pack(side=tk.LEFT)
        self.resId.pack(side=tk.LEFT)
        self.interfaceLabel.pack(side=tk.LEFT)
        self.interfaceOptions.pack(side=tk.LEFT)
        self.deviceLabel.pack(side=tk.LEFT)
        self.deviceOptions.pack(side=tk.LEFT)
        self.bdLabel.pack(side=tk.LEFT)
        self.baudRate.pack(side=tk.LEFT)
        self.communicationMenu.pack(side=tk.TOP)
# ------ comm status
        self.commStatus = tk.Canvas(self.frame, width=600, height=100,
                                    background='white',
                                    bd=0, highlightthickness=0)
        self.commButton = tk.Button(self.commStatus, text="Connect",
                                    command=self.configComm)
        self.commLabel = tk.Label(self.commStatus,
                                  text='Status: waiting...')
        self.commLabel.pack(side=tk.TOP)
        self.commButton.pack(side=tk.TOP)
        self.commStatus.pack(side=tk.TOP)
# ------ request title
        self.requestTitleMenu = tk.Canvas(self.frame, width=600, height=100,
                                          background='white',
                                          bd=0, highlightthickness=0)
        self.requestTitle = tk.Label(self.requestTitleMenu,
                                     text='Mount the request: ')
        self.requestTitle.pack(side=tk.TOP)
        self.requestTitleMenu.pack(side=tk.TOP)
# ------ request menu
        self.requestMenu = tk.Canvas(self.frame, width=600, height=400,
                                     background='white',
                                     bd=0, highlightthickness=0)
        self.services = {
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
        self.dataToRead = {
            'Read active diagnostic session': 0xF186,
            'Read system supplier identifier': 0xF18A,
            'Read ECU manufacturing date': 0xF18B,
            'Read ECU serial number': 0xF18C,
            'Read supplier ECU hardware number': 0xF192,
            'Read system supplier ECU HW version number': 0xF193,
            'Read system supplier ECU software number': 0xF194,
            'Read ODXFileDataIdentifier': 0xF19E,
            'Read enable/disable B messages': 0xFD11,
            'Read configured CAN1 baud rate': 0xFD12,
            'Read current CAN1 baud rate': 0xFD13,
            'Read CAN1 diagnostics messages IDs': 0xFD14,
            'Read object/filtered object message IDs': 0xFD15,
            'Read last configured single CAN message ID': 0xFD16,
            'Read radar ECU CAN message Ids': 0xFD17,
            'Read object/filtered object message prioritization': 0xFD18,
            'Read configured number of sent objects/filtered objects': 0xFD19,
            'Read antenna modulation combinations': 0xFD26,
            'Read CAN communication protocol': 0xFD27,
            'Read mounting position': 0xFD28,
            'Read current number of sent objects/filtered': 0xFD29,
            'Read zone configuration': 0xFD60,
            'Read layer': 0xFD61,
            'Read enable/disable object/filtered object and/or zone message': 0xFD62,  # noqa: E501
            'Read radar wave emission stop': 0xFD63,
            'Read output coordinate system': 0xFD64}
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
        self.dataOptions = {'Read Data': self.dataToRead,
                            'Write Data': self.dataToWrite}

        self.service = tk.StringVar(window)
        self.service.trace('w', self.updateData)
        self.serviceLabel = tk.Label(self.requestMenu, text='SID')
        self.serviceOptions = tk.OptionMenu(self.requestMenu, self.service,
                                            *self.services.keys())
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
        self.sFunction = tk.StringVar(self)
        self.sFunctionLabel = tk.Label(self.requestMenu, text='SubFn')
        self.sFunctionOptions = tk.OptionMenu(self.requestMenu, self.sFunction,
                                              '')
        self.sFunctionOptions['menu'].delete(0, tk.END)

        self.dataIdentifier = tk.StringVar(self)
        self.dIdentifierLabel = tk.Label(self.requestMenu, text='DID')
        self.dIdentifierOptions = tk.OptionMenu(self.requestMenu,
                                                self.dataIdentifier, '')
        self.dIdentifierOptions['menu'].delete(0, tk.END)

        self.dRecordLabel = tk.Label(self.requestMenu, text='DataRec')
        self.dataRecord = tk.Entry(self.requestMenu, bd=5, width=20,
                                   disabledbackground='silver',
                                   state=tk.DISABLED)

        self.B3 = tk.Button(self.requestMenu, text="Send",
                            command=self.sendRequest)
        # self.B3.config(state='disabled')
        self.serviceLabel.pack(side=tk.LEFT)
        self.serviceOptions.pack(side=tk.LEFT)
        self.sFunctionLabel.pack(side=tk.LEFT)
        self.sFunctionOptions.pack(side=tk.LEFT)
        self.dIdentifierLabel.pack(side=tk.LEFT)
        self.dIdentifierOptions.pack(side=tk.LEFT)
        self.dRecordLabel.pack(side=tk.LEFT)
        self.dataRecord.pack(side=tk.LEFT)
        self.B3.pack(side=tk.LEFT)
        self.requestMenu.pack(side=tk.TOP)
# ------ response menu
        self.responseMenu = tk.Canvas(self.frame, width=600, height=100,
                                      background='white',
                                      bd=0, highlightthickness=0)
        self.response = tk.Label(self.responseMenu,
                                 text='Response: ')
        self.response.pack(side=tk.TOP)
        self.responseMenu.pack(side=tk.TOP)
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

    def sendRequest(self):
        if self.service.get() == '':
            messagebox.showinfo("Error",
                                'Select a SID')
        else:
            if self.service.get() == 'Read Data':
                if self.dataIdentifier.get() != '':
                    message = (hex(self.services.get(self.service.get(), '')),
                               # self.sFunctions.get(self.sFunction.get(), ''),
                               hex(self.dataToRead.get(self.dataIdentifier.get(),  # noqa: E501
                                                       '')))
                    if tk.messagebox.askyesno('Confirm', "SID: " + self.service.get() + "\n" + "DID: " + self.dataIdentifier.get()):  # noqa: E501
                        self.response['text'] = 'Request: ' + str(message)
                        # print(message)
                else:
                    messagebox.showinfo("Error",
                                        'DID is missing')

            elif self.service.get() == 'Write Data':
                if self.dataRecord.get() != '' and self.dataIdentifier.get() != '':  # noqa: E501
                    message = (hex(self.services.get(self.service.get(), '')),
                               # hex(self.sFunctions.get(self.sFunction.get(), '')),  # noqa: E501
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
                message = (hex(self.services.get(self.service.get(), '')),
                           hex((self.sfOptions.get(self.service.get())).get(self.sFunction.get())))  # noqa: E501
                if tk.messagebox.askyesno('Confirm the content',
                                          "SID: " + self.service.get() + "\n" + "SubFn: " + self.sFunction.get()):  # noqa: E501
                    self.response['text'] = 'Request: ' + str(message)
                # print(hex((self.sfOptions.get(self.service.get())).get(self.sFunction.get())))  # noqa: E501
            else:
                if tk.messagebox.askyesno('Confirm the content',
                                          self.service.get()):
                    # self.response['text'] = 'Request: ' + str(message)
                    msg = self.a.send(self.services.get(self.service.get()))
                    '''if msg[0] == 0x7e:
                        msg[1] = 'Positive response '
                    else:
                        msg[1] = 'Negative response '''
                    self.response['text'] = 'Response: ' + str(msg)

    def configComm(self):
        reqId, resId = self.reqId.get(), self.resId.get()
        interface, device = self.interface.get(), self.device.get()
        baudrate = self.baudRate.get()
        aux = True
        msg = ''
        if not all(c in string.hexdigits for c in reqId) or reqId == '':
            msg = 'Invalid redId'
            aux = False
        else:
            reqId = int(reqId, 16)
        if not all(c in string.hexdigits for c in resId) or resId == '':
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
        if not all(c in string.digits for c in baudrate) or baudrate == '':
            msg = 'Invalid baudrate'
            aux = False
        if aux:
            try:
                self.a = Uds(reqId=reqId, resId=resId, interface=interface,
                             device=device, baudrate=baudrate)
                print(self.a)
                self.commLabel.config(text='Status: connected')
                self.serviceOptions.config(state='normal')
                self.B3.config(state='normal')
            except Exception:
                self.commLabel.config(text='Status: no connection')
                self.serviceOptions.config(state='disabled')
                self.B3.config(state='disabled')
                messagebox.showinfo('Error', 'There is no connection')
        else:
            messagebox.showinfo('Error', msg)


window = tk.Tk()
app = App(window)
app.mainloop()
