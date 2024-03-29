# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.http import JsonResponse

from import_export.admin import ExportMixin

from blanc_pages import block_admin

from addresses.admin import AddressInline
from notes.admin import NoteInline

from . import choices as people_choices
from .blocks.forms import NominateFormBlock
from .models import Person, Nominator, Nominee


@admin.register(Person)
class PersonAdmin(ExportMixin, admin.ModelAdmin):
    inlines = [
        AddressInline, NoteInline
    ]
    date_hierarchy = 'created_at'
    search_fields = (
        'first_name', 'last_name', 'life__first_name', 'life__last_name', 'email',
        'home_phone', 'mobile_phone',
    )
    list_display = (
        'first_name', 'last_name', 'reason', 'life', 'email', 'home_phone',
        'mobile_phone', 'hear_about_us', 'updated_at', 'created_at',
    )
    list_filter = ('reason',)
    fieldsets = (
        (
            'Person', {
                'fields': (
                    'first_name', 'last_name', 'life', 'reason', 'message',
                    'hear_about_us',
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
            'Meta data', {
                'classes': ('collapse',),
                'fields': (
                    'id', 'created_at', 'updated_at',
                )
            }
        ),
    )
    raw_id_fields = ('life',)

    readonly_fields = ('id', 'created_at', 'updated_at', 'is_agreed',)

    class Media:
        js = ('js/admin/addresses/addresses.js',)

    def get_queryset(self, request):
        qs = super(PersonAdmin, self).get_queryset(request)
        return qs.exclude(reason=people_choices.REASON_TYPE_WOULD_LIKE_TO_NOMINATE)

    def get_urls(self):
        urls = super(PersonAdmin, self).get_urls()
        extra_urls = [
            url(
                r'^(\d+)/add-note/$',
                self.add_note,
                name='persons-add-note'
            ),
            url(
                r'^(\d+)/add-address/$',
                self.add_address,
                name='persons-add-address'
            )
        ]
        return extra_urls + urls

    def get_inline_instances(self, request, obj=None):
        """ Update post url for AddressInline and NotesInline. """
        inline_instances = super(PersonAdmin, self).get_inline_instances(request, obj)
        if obj is not None:
            for inline in inline_instances:
                if isinstance(inline, AddressInline):
                    inline.dialog_data['post_url'] = reverse(
                        'admin:persons-add-address', args=(obj.id,)
                    )
                elif isinstance(inline, NoteInline):
                    inline.dialog_data['post_url'] = reverse(
                        'admin:persons-add-note', args=(obj.id,)
                    )
        return inline_instances

    def get_formsets_with_inlines(self, request, obj=None):
        if obj is None:
            return []
        return super(PersonAdmin, self).get_formsets_with_inlines(request, obj)

    def add_note(self, request, object_id):
        """ Add note for life. """
        context = {}
        obj = self.get_object(request, unquote(object_id))
        context = NoteInline.create_note(
            request, obj
        )
        return JsonResponse(context)

    def add_address(self, request, object_id):
        """ Add address for person. """
        obj = self.get_object(request, unquote(object_id))
        context = AddressInline.create_address(
            request, obj
        )

        return JsonResponse(context)


class NomineeInline(admin.StackedInline):
    model = Nominee
    max_num = 1
    readonly_fields = (
        'first_name', 'country', 'relation', 'why_help', 'what_need'
    )


@admin.register(Nominator)
class NominatorAdmin(PersonAdmin):
    list_filter = ()
    inlines = [
        NomineeInline, NoteInline
    ]
    fieldsets = (
        (
            'Person', {
                'fields': (
                    'first_name', 'last_name', 'life', 'message',
                    'hear_about_us', 'is_agreed',
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
            'Meta data', {
                'classes': ('collapse',),
                'fields': (
                    'id', 'created_at', 'updated_at',
                )
            }
        ),
    )

    def get_queryset(self, request):
        qs = super(PersonAdmin, self).get_queryset(request)
        return qs.filter(reason=people_choices.REASON_TYPE_WOULD_LIKE_TO_NOMINATE)


block_admin.site.register((NominateFormBlock))
block_admin.site.register_block(NominateFormBlock, 'Forms')
