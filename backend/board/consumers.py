from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .services import board_to_json, add_board_obj, undo, redo, has_access


class BoardConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.board_id = None

    async def connect(self):
        self.board_id = self.scope["url_route"]["kwargs"]["board_id"]
        self.user = self.scope['user']
        await self.accept()
        if not await self.has_access():
            await self.close(code=4003)
            return
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.send_initial_data()

    @database_sync_to_async
    def has_access(self):
        board_name = (dict((x.split('=') for x in self.scope['query_string'].decode().split("&")))).get('name',
                                                                                                             None)
        return has_access(self.board_id, self.user, board_name)

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

    async def send_update_board_data(self):
        payload = await self.get_board_data()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_board_objects",
                "content": {"type": "UPDATE_BOARD",
                            "data": payload,
                            },
            }
        )

    @database_sync_to_async
    def get_board_data(self):
        payload = board_to_json(board_id=self.board_id, user_id=self.user.pk)
        return payload

    @database_sync_to_async
    def add_object(self, object_data):
        obj = add_board_obj(self.board_id, object_data, self.user)
        return obj.pk

    @database_sync_to_async
    def undo_object(self, board_obj):
        undo(board_obj)

    @database_sync_to_async
    def redo_object(self, board_obj):
        redo(board_obj)

    async def send_board_objects(self, event):
        await self.send_json(event['content'])

    async def receive_json(self, content, **kwargs):
        if content.get('method') == 'undo':
            await self.undo_object(content)
            await self.send_update_board_data()
        elif content.get('method') == 'redo':
            await self.redo_object(content)
            await self.send_update_board_data()
        else:
            board_obj = await self.add_object(content)
            content["id"] = str(board_obj)
            content["user"] = str(self.user.username)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_board_objects",
                    "content": {"type": "ADD_OBJECT",
                                "data": {"objects": [content]}},
                },
            )
