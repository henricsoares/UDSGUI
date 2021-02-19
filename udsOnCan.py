import can
from udsoncan.connections import PythonIsoTpConnection, IsoTPSocketConnection  # noqa: F401 E501
from udsoncan.client import Client  # noqa: F401
import isotp
from udsoncan import Response, Request, services  # noqa: F401

tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits,
                        txid=0x18DA2AF1, rxid=0x18DAFA2A)
bus = can.interface.Bus(bustype='pcan', channel='PCAN_USBBUS1', bitrate=500000)
stack = isotp.CanStack(bus=bus, address=tp_addr)
conn = PythonIsoTpConnection(stack)
with Client(conn, request_timeout=1,
            config={'exception_on_unexpected_response': False}) as client:
    try:
        conn.send(b'\x22\xFD\x12')
        payload = conn.wait_frame(timeout=1)
        response = Response.from_payload(payload)
        print(response, (response.data)[2])
    except Exception as e:
        print(e)
