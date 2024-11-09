# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from users.models import Project
from users.models import Comment  # Import your Comment model
from django.utils import timezone
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.user = self.scope["user"]

        # Only allow authenticated users to join
        if not self.user.is_authenticated:
            await self.close()
            return

        # Verify that the user is a collaborator on the project
        can_join = await self.check_collaborator_permission(self.project_id, self.user)
        if not can_join:
            await self.close()
            return

        # Join the room if permission is granted
        self.room_group_name = f'chat_{self.project_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()  # Remove any extra whitespace

        # Only proceed if the message is not empty
        if message:
            # Save the message to the database
            await self.save_message(self.project_id, self.user, message)

            # Broadcast message with user info to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']  # Ensure this matches the key in `group_send`

        # Send the message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,  # Include user here to send to the frontend
        }))

    @database_sync_to_async
    def check_collaborator_permission(self, project_id, user):
        try:
            project = Project.objects.get(id=project_id)
            return project.user == user or user in project.collaborators.all()
        except Project.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, project_id, user, message):
        """ Save the message to the database """
        project = Project.objects.get(id=project_id)
        Comment.objects.create(
            project=project,
            user=user,
            text=message,
            timestamp=timezone.now().timestamp()
        )
