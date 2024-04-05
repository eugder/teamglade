from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
# from django.utils.html import mark_safe
# from markdown import markdown
from os.path import basename

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
    # files = models.FileField(upload_to='uploads/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(RoomUser, on_delete=models.CASCADE, related_name='topics')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="topics")
    was_read_by = models.ManyToManyField(RoomUser, related_name='read_topics')

    # def get_message_as_markdown(self):
    #     return mark_safe(markdown(self.message, safe_mode='escape'))

    def __str__(self):
        return self.title

class File(models.Model):
    file = models.FileField(upload_to='uploads/')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='files')

    # file name without path for topic template
    def filename(self):
        return basename(self.file.name)


# Deletes file when File instance is deleting
@receiver(pre_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
