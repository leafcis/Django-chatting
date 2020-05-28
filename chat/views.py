from django.shortcuts import render
from django.utils.safestring import mark_safe
from .models import Room
import json

def index(request):
  room_list=Room.objects.all()
  context = {'room_list':room_list}
  return render(request, 'index.html', context)

def room(request, room_name):
  return render(request, 'room.html', {
    'room_name_json': mark_safe(json.dumps(room_name))
  })
# Create your views here.
