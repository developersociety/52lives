# -*- coding: utf-8 -*-

from blanc_pages.layouts import PageLayout
from blanc_pages import columns
from blanc_pages import pages
from blanc_pages import get_page_model


@pages.register(get_page_model())
class Default(PageLayout):
    intro = columns.Column(width=960)
    content = columns.Column('Main content', width=960)

    class Meta:
        template = 'blanc_pages/default.html'
        verbose_name = 'Default'


@pages.register(get_page_model())
class HomePage(PageLayout):
    intro = columns.Column(width=960)
    content = columns.Column('Main content', width=960)
    left_side = columns.Column('Left side', width=320)


@pages.register(get_page_model())
class HomePagePopUp(HomePage):
    testing = columns.Column('Left side', width=320)
