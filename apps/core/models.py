# -*- coding: utf-8 -*-

from django.db import models


class TestOne(models.Model):
    lol = models.CharField(max_length=230)
    boom = models.CharField(max_length=230)
    zoom = models.CharField(max_length=230)

    class Meta:
        abstract = True


class TestTwo(TestOne):
    first = models.CharField(max_length=230)
    second = models.CharField(max_length=230)
    third = models.CharField(max_length=230)
