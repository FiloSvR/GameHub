import logging

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group

from rest_framework import viewsets

from game.models import Game

from .serializers import UserSerializer, GameSerializer

logger = logging.getLogger(__name__)

# Create your views here.

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

class DeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.get(name='Developer').user_set.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

class GameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'title'
