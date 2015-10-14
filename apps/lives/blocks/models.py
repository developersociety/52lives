# -*- coding: utf-8 -*-

from django.db import models

from blanc_pages.models.blocks import BaseBlock


class LatestLivesBlock(BaseBlock):
    number_of_lives = models.PositiveIntegerField(default=10)

    class Meta:
        verbose_name = 'Latest lives'


class LiveBlock(BaseBlock):
    life = models.ForeignKey(
        'lives.Life',
        blank=True,
        null=True,
        limit_choices_to={'number__isnull': False}
    )

    class Meta:
        verbose_name = 'Life'
