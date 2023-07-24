from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class RoomUser(AbstractUser):
    invite_code = models.CharField(max_length=10)

class Room(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(RoomUser, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=160)
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(RoomUser, on_delete=models.CASCADE, related_name='topics')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="topics")
    was_read_by = models.ManyToManyField(RoomUser, related_name='read_topics')

    def __str__(self):
        return self.title