from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    tag = models.CharField(max_length=30, unique=True)
    bio = models.TextField(blank=True, null=True, max_length=256)
    avatar = models.ImageField(upload_to='media/avatars/', blank=True, null=True, default="media/deafualt_avatar/default.png")


class ChatRoom(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chat = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.sender.username}"


class WaitingUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

