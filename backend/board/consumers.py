from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .services import board_to_json, add_board_obj


class BoardConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope["url_route"]["kwargs"]["board_id"]
        await self.accept()
        await self.send_initial_data()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    @staticmethod
    def get_group_name(board_id):
        return f"board-{board_id}"

    @property
    def group_name(self):
        if not self.board_id:
            raise ValueError("No board id")
        return self.get_group_name(self.board_id)

    async def send_initial_data(self):
        payload = await self.get_board_data()
        return await self.send_json({"type": "INITIAL_DATA", "data": payload})

    @database_sync_to_async
    def get_board_data(self):
        payload = board_to_json(board_id=self.board_id)
        return payload

    @database_sync_to_async
    def add_object(self, object_data):
        obj = add_board_obj(self.board_id, object_data)
        return obj.pk

    async def send_new_board_object(self, event):
        await self.send_json(event['content'])

    async def receive_json(self, content, **kwargs):
        board_obj = await self.add_object(content)
        content["id"] = str(board_obj)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_new_board_object",
                "content": {"type": "ADD_OBJECT", "data": {"object": content}},
            },
        )
