from django.contrib import admin

# Register your models here.
# -*- coding: utf-8 -*-

from blanc_pages import block_admin

from .blocks.models import Video, TwoColumnBlock


block_admin.site.register(Video)
block_admin.site.register_block(Video, 'Video')

block_admin.site.register(TwoColumnBlock)
block_admin.site.register_block(TwoColumnBlock, 'Two Colummn Block')