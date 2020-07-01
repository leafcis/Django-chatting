from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import random
from .models import Room

class ChatConsumer(AsyncWebsocketConsumer):
    def con_room(self, room):
        try:
            room = Room.objects.get(title=room)
            room.member = room.member + 1
            room.save()
            if(room.member <= 8):
                return True
            else:
                return False

        except Room.DoesNotExist:
            room = Room(title=room, member=1)
            room.save()
            return True

    def discon_room(self, room):
        room = Room.objects.get(title=room)
        room.member = room.member - 1
        if(room.member == 0):
            room.delete()
        else:
            room.save()

    async def connect(self):
        self.scope["session"]["seed"] = random.randint(1, 1000)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        self.flag = await database_sync_to_async(self.con_room)(self.room_name)

        if(self.flag == False):
            await self.close()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'state': 'join',
                'message': '{0} 님이 채팅에 들어오셨습니다.',
                'id': self.scope["session"]["seed"],
                'username': self.scope["user"].username,
                'isLogin': self.scope["user"].is_authenticated,
            }
        )

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await database_sync_to_async(self.discon_room)(self.room_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'state': 'leave',
                'message': '{0} 님이 채팅을 나가셨습니다.',
                'id': self.scope["session"]["seed"],
                'username': self.scope["user"].username,
                'isLogin': self.scope["user"].is_authenticated,
            }
        )

    async def receive(self, bytes_data=None, text_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'id': self.scope["session"]["seed"],
                'username': self.scope["user"].username,
                'isLogin': self.scope["user"].is_authenticated,
            }
        )

    async def chat_message(self, event):
        if('state' not in event.keys()):
            message = event['message']
            id = event['id']
            username = event['username']
            await self.send(text_data=json.dumps({
                'message': message,
                'id': id,
                'selfId' : self.scope["session"]["seed"],
                'username': username,
                'isLogin': self.scope["user"].is_authenticated,
            }))
        else:
            _id = event['id']
            message = event['message']
            username = event['username']
            id = "손님" + str(event['id'])
            if(event['isLogin'] is True):
                id = username
            await self.send(text_data=json.dumps({
                'id': _id,
                'selfId': self.scope["session"]["seed"],
                'etc_message': message.format(id),
                'username': username,
                'isLogin': self.scope["user"].is_authenticated,
            }))