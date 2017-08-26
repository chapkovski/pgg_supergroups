from otree.api import (
    models as m, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
# from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from django.forms import modelformset_factory,  inlineformset_factory, ModelForm

from .models import  Player, Group, SuperGroup



class Contribute(Page):

    form_model = models.Player
    form_fields = ['contribution']


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    pass

page_sequence =[
    Contribute,
    ResultsWaitPage,
    Results
]
