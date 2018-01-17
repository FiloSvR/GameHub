import pdb

import logging
import json

from django.db.models import Max
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.models import User

from .models import Game, GamePlayed, PaymentDetail
from .utils import get_checksum
from .forms import UploadGameForm
from .decorators import group_required, game_player_required
import accounts.urls

logger = logging.getLogger(__name__)

# Create your views here.

@require_http_methods(('GET', 'HEAD'))
def details(request, game):
    """Presents a game for buying.

    At the moment this view only responds with a string describing the game object.

    Args:
        game (int): The private key of the game.

    :statuscode 200: Success.
    :statuscode 404: Game not found.
    """

    try:
        game = Game.objects.get(pk=game)
    except:
        return HttpResponseNotFound('The game you requested could not found!')
    game.increment_viewcount()
    game_owner = False
    if request.user.is_authenticated:
        games = request.user.gameplayed_set.all()
        if game in list(map(lambda x: x.game, games)):
            game_owner = True
    context = {'game': game, 'game_owner': game_owner}
    return render(request, template_name='game/game.html', context=context)

@require_http_methods(('GET', 'HEAD'))
def search(request):
    """Gives the result page for a search query.

    The following context is provided to the template:

    - hits: queryset containing all the models for the current page in the query.
    - page: the number of the current page.
    - numpages: the total number of pages found in the query.
    - pagelist: this is an iterable producing the indexes of pages for the pagination thingy.
    - query: the original query string.

    GET Params:

    - q: The search query string. If not provided it finds all games.
    - p: The page number.

    The number of games in a response is limited by a maximum page size. Page numbers
    start from 1. If not provided it defaults to 1.

    :statuscode 200: Success.
    :statuscode 400: Bad request if page number is 0 or lower.

    .. todo:: Make the template presentable.
    """

    pagelen = 20
    npaginate = 4

    q = request.GET.get('q', default=None)
    p = int(request.GET.get('p', default=1))

    if p <= 0:
        return HttpResponseBadRequest()

    qset = Game.search(q)
    qlen = len(qset)
    numpages = (qlen + pagelen - 1) // pagelen
    qset = qset[(p - 1) * pagelen : p * pagelen]
    
    #Assemble pagelist. This must be done here because django templates do not
    #support numeric for loops.
    nlpages = 8
    if nlpages // 2 + 1 >= p:
        pagelist = range(1, nlpages + 2 if nlpages < numpages else numpages + 1)
    elif p + nlpages // 2 >= numpages:
        pagelist = range(numpages - nlpages if numpages > nlpages else 1, numpages + 1)
    else:
        pagelist = range(p - nlpages // 2, p + nlpages // 2 + 1)

    return render(request,
        template_name='game/search.html',
        context={
            'hits': qset,
            'page': p,
            'numpages': numpages,
            'query': q,
            'pagelist': pagelist
        })

#ONLY Developer can upload the game and of course superuser
@group_required('Developer')
def upload(request):
    """Provides the upload functionality.

    On get it presents a form for uploading a game. On post it processes that form,
    and either redirects with an error or returns a response confirming the upload.

    The following context is provided to the template:
      - form: templates/game/upload.html.
      - errors: a dict containing the errors.

    The form used is a standard ModelForm with nothing special.

    The errors dict used in the templates is copied from Form.errors in case of a
    validation error. The view then redirects to itself with a GET request. The
    errors dict is stored in the current session, in field 'errors'. This field in
    the session is cleared on a GET request.

    :statuscode 200: Success.
    :statuscode 302: Redirection in case of either invalid authorization, or a validation error.

    .. todo:: Upon successful upload it should redirect somewhere, not just give a string response.
    """

    if 'errors' in request.session:
        errors = request.session['errors']
        del request.session['errors']
    else:
        errors = None

    if request.method == 'POST':
        form = UploadGameForm(request.POST, request.FILES)
        if form.is_valid():
            new_game = form.save(commit=False)
            new_game.developer = request.user
            new_game.save()
            #adds the developer as a player allowing to play game without buying
            played_game = GamePlayed.objects.create(gameScore=0)
            played_game.game = new_game
            played_game.save()
            PaymentDetail.objects.create(game_played = played_game, cost=new_game.price, user=request.user)
            return HttpResponse('Upload successful!')
        else:
            request.session['errors'] = form.errors
            return HttpResponseRedirect(reverse('game:upload'))
    else:
        form = UploadGameForm()
        return render(request, 'game/upload.html', {'form': form, 'errors': errors})


@require_http_methods(('GET', 'HEAD'))
@login_required
def purchase(request, game):
    try:
        game = Game.objects.get(pk=game)
    except:
        return HttpResponseNotFound()
    games = request.user.gameplayed_set.all()
    if game in list(map(lambda x: x.game, games)):
        messages.add_message(request, messages.INFO, 'You have already purchased the game!')
        return redirect(reverse('game:detail', kwargs={'game':game.id}))
    message = "pid={}&sid={}&amount={}&token={}".format(game.id, settings.SELLER_ID, game.price, settings.PAYMENT_KEY)
    checksum = get_checksum(message)
    context =  {'game': game.id, 'checksum': checksum, 'pid': game.id, 'sid': settings.SELLER_ID, 'amount': game.price }
    return render(request, "game/buy.html", context=context)

@require_http_methods(('GET', 'HEAD'))
def process_purchase(request):
    pid = request.GET.get('pid')
    ref = request.GET.get('ref')
    result = request.GET.get('result')
    checksum = request.GET.get('checksum')
    message = "pid={}&ref={}&result={}&token={}".format(pid, ref, result, settings.PAYMENT_KEY)
    if get_checksum(message) == checksum:
        buy_game = GamePlayed.objects.create(gameScore=0)
        buy_game.game = Game.objects.get(pk=pid)
        buy_game.game.increment_sellcount()
        buy_game.save()
        PaymentDetail.objects.create(game_played = buy_game, cost=buy_game.game.price, user=request.user)
        return redirect(reverse('game:detail', kwargs={'game':buy_game.game.id}))
    else:
        return HttpResponse('sorry, you!')

@require_http_methods(('GET', 'HEAD'))
def highscore(request, game):
    if request.is_ajax():
        game = Game.objects.get(pk=game)
        highscore = GamePlayed.objects.filter(game=game).aggregate(Max('gameScore'))
        return HttpResponse(highscore['gameScore__max'])
    else:
        return HttpResponseBadRequest('Only ajax')

@require_http_methods(('POST', 'HEAD'))
@csrf_exempt #no csrf for this post
@game_player_required #only the game player
def update_played_game(request, game):
    """Fetch the game based on the game id and users from GamePlayed tables, &
    responds based on the messageType received in json data passed with ajax
    request. If the messageType is 'LOAD_REQUEST', it constructs the json data
    and send as response. So, it is with when ERROR messageType is received.
    """
    if request.is_ajax():
        game_played = GamePlayed.objects.get(users__pk=request.user.pk, game__id=game)
        data = request.POST.get('data')
        data_dict = json.loads(data)
        if data_dict['messageType'] == 'SAVE':
            game_played.gameState = data
            #update highscores if score of saved game is higher
            if data_dict['gameState']['score'] > game_played.gameScore:
                game_played.gameScore = data_dict['gameState']['score']
            game_played.save()
        if data_dict['messageType'] == 'SCORE':
            game_played.gameScore = data_dict['score']
            game_played.save()
        if data_dict['messageType'] == 'LOAD_REQUEST':
            try:
                data = json.loads(game_played.gameState)
                data['messageType'] = 'LOAD'
                return HttpResponse(json.dumps(data), content_type="application/json")
            except:
                return HttpResponseBadRequest('error')
        return HttpResponse('Great Job So Far')
    else:
        return HttpResponseBadRequest('Only ajax')

class GameUpdateView(UpdateView):
    model = Game
    form_class = UploadGameForm
    def post(self, request, game):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            new_game = form.save(commit=False)
            new_game.developer = request.user
            new_game.save()
            return redirect('accounts:home') #redirects to the profiledetail view later to do
        else:
            return render(request, template_name='game/upload.html', context={'form': form })
    def get(self, request, game):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return render(request, template_name='game/upload.html', context={'form': form})

    def get_object(self):
        return get_object_or_404(Game, pk=self.kwargs['game'])

class GameDeleteView( DeleteView):
    model = Game
    template_name = 'game/delete.html'

    def get_success_url(self):
        return reverse_lazy('accounts:detail', kwargs={'pk': self.object.developer.id})

    def get_object(self):
        return get_object_or_404(Game, pk=self.kwargs['game'])

@require_http_methods(('POST'))
@csrf_exempt
@game_player_required
def rate(request, game):
    if request.is_ajax():
        try:
          rating = int(request.POST.get('rating'))
          assert rating >= 1 and rating <= 5
        except:
          return HttpResponseBadReqeust('Invalid rating provided')
        
        try:
          game_played = GamePlayed.objects.get(
            users__pk=request.user.pk,
            game__id=game
          )
        except:
          return HttpResponseNotFound()
        
        game_played.set_rating(rating)
        return HttpResponse(str(rating))
    else:
        return HttpResponseBadRequest('Only ajax')
