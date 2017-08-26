from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import csv

from django.db import models as djmodels

author = 'Your name here'

doc = """
Simple public goods game
"""
SUPERGROUP_NUM_ERR = 'Wrong number of players per supergroup'


class Constants(BaseConstants):
    name_in_url = 'public_goods_simple'
    players_per_group = 3
    players_per_supergroup = 6
    groups_per_supergroup = int(players_per_supergroup / players_per_group)
    assert players_per_supergroup % players_per_group == 0, \
        SUPERGROUP_NUM_ERR
    num_rounds = 10

    endowment = c(100)
    multiplier = 1.8


def slice_list(input):
    ppg = Constants.players_per_group
    output = [input[i:i + ppg] for i in range(0, len(input), ppg)]
    for o in output:
        assert len(o) == ppg, SUPERGROUP_NUM_ERR
    return output


def chunkify(lst, n):
    return [lst[i::n] for i in range(n)]


class Subsession(BaseSubsession):
    def creating_session(self):
        supergroups_n = int(len(self.get_players()) / Constants.players_per_supergroup)
        chunked_players = chunkify(self.get_players(), supergroups_n)
        for i, s in enumerate(chunked_players):
            supergroup = self.supergroups.create(s_id=i)
            supergroup.save()
            for p in s:
                supergroup.players.add(p)

        new_matrix = []
        for s in self.supergroups.all():
            new_matrix.extend(s.get_shuffled_groups())
        self.set_group_matrix((new_matrix))
        for s in self.supergroups.all():
            s.random_player.is_loser=True



class SuperGroup(djmodels.Model):
    class Meta:
        unique_together = ('s_id', 'subsession')

    s_id = models.IntegerField()
    subsession = djmodels.ForeignKey(to=Subsession,
                                     related_name='supergroups')

    def get_shuffled_groups(self):
        players = list(self.players.all())
        random.shuffle(players)
        return chunkify(players, Constants.groups_per_supergroup)
    @property
    def random_player(self):
        players = list(self.players.all())
        return random.choice(players)

    def __str__(self):
        return "Supergroup N{}".format(self.s_id)


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    supergroup = djmodels.ForeignKey(SuperGroup, null=True, related_name='groups')


    def set_payoffs(self):
        self.total_contribution = sum(
            [p.contribution for p in self.get_players()])
        self.individual_share = self.total_contribution * Constants.multiplier / Constants.players_per_group
        for p in self.get_players():
            p.payoff = Constants.endowment - p.contribution + self.individual_share
            if p.is_loser:
                p.payoff_sanction = abs(p.deviation_focalpoint * 1.25)



class Player(BasePlayer):
    payoff_sanction = models.CurrencyField(initial=0)
    deviation_focalpoint = models.CurrencyField(initial=0)
    is_loser=models.BooleanField()
    contribution = models.CurrencyField(min=0, max=Constants.endowment)
    supergroup = djmodels.ForeignKey(SuperGroup, null=True, related_name='players')
