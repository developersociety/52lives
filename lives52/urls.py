# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from blanc_pages import block_admin

from two_factor.admin import AdminSiteOTPRequired

if not settings.DEBUG:
    admin.site.__class__ = AdminSiteOTPRequired

urlpatterns = [
    url(r'^news/', include('blanc_basic_news.urls', namespace='blanc_basic_news')),
    url(r'^lives/', include('lives.urls', namespace='lives')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blockadmin/', include(block_admin.site.urls)),
    url(r'^nominate/', include('people.urls', namespace='nominate')),
    url(r'^12lives/', include('companies.urls', namespace='companies')),
    url(r'', include('two_factor.urls', 'two_factor')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', name='logout'),
]


# Make it easier to see a 404 page under debug
if settings.DEBUG:
    from django.views.defaults import page_not_found

    urlpatterns += [
        url(r'^404/$', page_not_found),
    ]

# Only enable debug toolbar if it's an installed app
if apps.is_installed('debug_toolbar'):
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

# Serving static/media under debug
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
