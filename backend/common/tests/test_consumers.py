from django.test import SimpleTestCase
from channels.testing import WebsocketCommunicator
from ..consumers import MicrocontrollerConsumer
from backend.asgi import application


class MicrocontrollerConsumerTestCase(SimpleTestCase):
    async def test_my_consumer(self):
        communicator = WebsocketCommunicator(application, "microcontroller/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test sending text
        await communicator.send_json_to({"hello": "world"})
        response = await communicator.receive_json_from()
        self.assertEqual(response, {"hello": "world"})

        await communicator.disconnect()
