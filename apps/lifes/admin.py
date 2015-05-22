# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.http import JsonResponse

from sorl.thumbnail.admin import AdminImageMixin

from addresses.admin import AddressInline
from notes.admin import NoteInline
from nominators.models import Nominator

from .models import Life


class NominatorInline(admin.TabularInline):
    model = Nominator
    can_delete = False
    extra = 0
    min_num = 0
    readonly_fields = (
        'title', 'first_name', 'last_name', 'email', 'home_phone', 'mobile_phone', 'reason',
        'message', 'hear_about_us',
    )

    def has_add_permission(self, request):
        return False


@admin.register(Life)
class LifeAdmin(AdminImageMixin, admin.ModelAdmin):
    inlines = [
        NominatorInline, AddressInline, NoteInline
    ]
    date_hierarchy = 'created_at'
    search_fields = ('first_name', 'last_name', 'number', 'request',)
    list_display = (
        'get_full_name', 'number', 'request', 'home_phone', 'mobile_phone', 'is_published',
        'created_at', 'updated_at',
    )
    list_filter = ('is_published',)
    fieldsets = (
        (
            'Life', {
                'fields': (
                    'title', 'first_name', 'last_name', 'number',
                    'image', 'is_published',
                )
            }
        ),
        (
            'About', {
                'classes': ('collapse',),
                'fields': (
                    'content', 'request',
                )
            }
        ),
        (
            'Contacts', {
                'classes': ('collapse',),
                'fields': (
                    'email', 'home_phone', 'mobile_phone',
                )
            }
        ),

        (
            'Approved information', {
                'classes': ('collapse',),
                'fields': (
                    'summary', 'thank_you',
                )
            }
        ),
        (
            'Meta data', {
                'classes': ('collapse',),
                'fields': (
                    'id', 'created_at', 'updated_at',
                )
            }
        ),
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'number',)

    def get_urls(self):
        urls = super(LifeAdmin, self).get_urls()
        life_urls = [
            url(
                r'^(\d+)/add-note/$',
                self.add_note,
                name='life-add-note'
            ),
            url(
                r'^(\d+)/add-address/$',
                self.add_address,
                name='life-add-address'
            )
        ]
        return life_urls + urls

    def get_inline_instances(self, request, obj=None):
        """ Update post url for AddressInline. """
        inline_instances = super(LifeAdmin, self).get_inline_instances(request, obj)
        if obj is not None:
            for inline in inline_instances:
                if isinstance(inline, AddressInline):
                    inline.dialog_data['post_url'] = reverse(
                        'admin:life-add-address', args=(obj.id,)
                    )
                elif isinstance(inline, NoteInline):
                    inline.dialog_data['post_url'] = reverse(
                        'admin:life-add-note', args=(obj.id,)
                    )
        return inline_instances

    def get_formsets_with_inlines(self, request, obj=None):
        if obj is None:
            return []
        return super(LifeAdmin, self).get_formsets_with_inlines(request, obj)

    def add_note(self, request, object_id):
        """ Add note for life. """
        context = {}
        obj = self.get_object(request, unquote(object_id))
        context = NoteInline.create_note(
            request, obj
        )
        return JsonResponse(context)

    def add_address(self, request, object_id):
        """ Add address for life. """
        obj = self.get_object(request, unquote(object_id))
        context = AddressInline.create_address(
            request, obj
        )
        return JsonResponse(context)


