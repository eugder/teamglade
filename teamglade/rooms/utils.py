# Dummy data fill DB (for run in shell)

from rooms.models import RoomUser, Room, Topic

user = RoomUser.objects.filter(username='tu').get()

room = Room.objects.get(created_by=user)

for i in range(50):
    title = 'Pagination topics test #{}'.format(i)
    topic = Topic.objects.create(title=title, message="ok", room=room, created_by=user)
