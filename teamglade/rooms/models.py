from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
# from django.utils.html import mark_safe
# from markdown import markdown

class RoomUser(AbstractUser):
    invite_code = models.CharField(max_length=10)
    member_of = models.ForeignKey('Room', null=True, on_delete=models.CASCADE, related_name="members")

class Room(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(RoomUser, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    files = models.FileField(upload_to='uploads/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(RoomUser, on_delete=models.CASCADE, related_name='topics')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="topics")
    was_read_by = models.ManyToManyField(RoomUser, related_name='read_topics')

    # def get_message_as_markdown(self):
    #     return mark_safe(markdown(self.message, safe_mode='escape'))

    def __str__(self):
        return self.title