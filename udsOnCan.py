from can.interface import Bus
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import isotp
from udsoncan import Response

tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits,
                        txid=0x18DA2AF1, rxid=0x18DAFA2A)
bus = Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)
stack = isotp.CanStack(bus=bus, address=tp_addr)
conn = PythonIsoTpConnection(stack)
with Client(conn, request_timeout=1,
            config={'exception_on_unexpected_response': False}) as client:
    try:
        client.send(b'\x22\xFD\x12')
        payload = client.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        print(response.data)
    except Exception as e:
        print(e)
