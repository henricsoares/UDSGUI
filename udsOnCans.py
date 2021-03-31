from can.interface import Bus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import isotp
from udsoncan import Response
import securityAlgo as sec
from time import sleep

tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits,
                        txid=0x18DA2AF1, rxid=0x18DAFA2A)
bus = Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)
stack = isotp.CanStack(bus=bus, address=tp_addr)
conn = PythonIsoTpConnection(stack)
with Client(conn, request_timeout=1,
            config={'exception_on_unexpected_response': False}) as client:
    try:
        conn.send(b'\x10\x03')
        payload = conn.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        print(response)
        conn.send(b'\x27\x63')
        payload = conn.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        print('key: ' + response.data.hex()[2:])
        seed = (response.data.hex()[2:])
        sA = sec.securityAlgo(seed, 'series')
        sleep(.1)
        print('calculated key: ' + (sA.calculatedKey).hex())
        conn.send(b'\x27\x64' + sA.calculatedKey)
        payload = conn.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        response = str(response).split('<')
        response = (response[1].split('-'))[0]
        print(response)
        conn.send(b'\x2e\xfd\x28\x7a\x98\x33\x88\xb7\x98\xb7\x98\xb7\x98\xb7\x98\xb7\x98\xb7\x98\x01\xf4')  # noqa: E501
        payload = conn.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        print(response)

    except Exception as e:
        print(e)
