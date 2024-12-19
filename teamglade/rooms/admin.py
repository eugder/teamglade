from django.contrib import admin
from .models import RoomUser, Room, Topic, File

class FileInline(admin.TabularInline):
    model = File


class Admin(admin.ModelAdmin):
    inlines = [
        FileInline,
    ]

admin.site.register(RoomUser)
admin.site.register(Room)
admin.site.register(Topic, Admin)
