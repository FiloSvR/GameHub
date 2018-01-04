import logging
import re
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

logger = logging.getLogger(__name__)

# Create your models here.

class Game(models.Model):
    """Game model

    referr to README.md for database schema.

    :members: title, url, description, gameimage

    .. todo::
        Relations with user models.
    """

    title       = models.TextField(max_length=300, unique=True)
    developer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    url         = models.URLField()
    price       = models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField()
    gameimage   = models.ImageField(null=True, blank=True, upload_to='game/')
    viewcount = models.PositiveIntegerField(default=0)

    def increment_viewcount(self):
        self.viewcount += 1
        self.save()
    @classmethod
    def create(cls, title, url, developer, price = 0.0, description='', gameimage=None, viewcount=0):
        """Creates an object. Use this function instead of calling the class
        constructor.
        """

        game = cls(
            title=title,
            url=url,
            price=price,
            developer = developer,
            description=description,
            gameimage=gameimage,
            viewcount=viewcount
        )
        return game

    @classmethod
    def search(cls, q):
        """Searches for games in the database.

        Args:
            q (str):
                The search query string. If None then it fetches all games from database

        Return:
            A queryset containing all the found games.
        """

        if q is None:
            return cls.objects.all()
        else:
            qwords = map(lambda m: m[0] if len(m[0]) > 0 else m[1],
                re.findall(r'"(.+)"|(\S+)', q))
            query = Q()
            for word in qwords:
                query = query & (
                    Q(title__contains=word) |
                    Q(description__contains=word))

            return cls.objects.all().filter(query)

    def __str__(self):
        return 'Game {0}, title: {1}, url: {2}'.format(
            self.pk,
            self.title,
            self.url
        )


class GamePlayed(models.Model):
    """GamePlayed model - when a user buys a game, the game is added to the
    GamePlayed database with gameState field empty, but users field with the
    user who bought the game.
    After the subsequent games, only the gameState for the user is updated.

    For storing extra information -how much a user paid for game (if needed),
    a middle model could be used in many to many relationship
    as referred to README.md for database schema.

    :members: game, gameScore, gameState, users

    """

    game = models.ForeignKey(Game, null=True, on_delete=models.SET_NULL)
    gameScore = models.IntegerField()
    gameState = models.TextField(default="{''}")
    users = models.ManyToManyField(User)

    def __str__(self):
        if (self.game):
            gametitle = self.game.title
        else:
            gametitle = 'Game Deleted'
        return 'Game {0}, GameState: {1}'.format(
            gametitle,
            self.gameState
        )
