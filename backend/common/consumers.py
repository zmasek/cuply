from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from asgiref.sync import async_to_sync
import json


class MicrocontrollerConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'events',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print("Closed websocket with code: ", close_code)
        await self.channel_layer.group_discard(
            'events',
            self.channel_name
        )
        await self.close()

    async def receive_json(self, content):
        print("Received event: {}".format(content))
        await self.send_json(content)

    # is this used?
    async def display_reading(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send_json(json.loads(message))
