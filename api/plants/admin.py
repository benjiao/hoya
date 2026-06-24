from django.contrib import admin
from django.db.models import CharField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce, Concat
from unfold.admin import ModelAdmin, TabularInline

from unfold.contrib.filters.admin import AllValuesCheckboxFilter, RangeDateFilter

from .admin_filters import (
    LastRepottedRangeFilter,
    LastWateredRangeFilter,
    LocationDropdownFilter,
    UserDropdownFilter,
)
from .forms import LocationChoiceField, location_queryset, LOCATION_SELECT_RELATED
from .models import Location, Plant, PlantImage, PlantCareLog

_PATH_SORT_SEP = Value('\x1f')
_PATH_SORT_EMPTY = Value('')


def annotate_fk_path_sort(queryset, relation_prefix, annotation_name):
    return queryset.annotate(**{
        annotation_name: Concat(
            Coalesce(f'{relation_prefix}__parent__parent__name', _PATH_SORT_EMPTY),
            _PATH_SORT_SEP,
            Coalesce(f'{relation_prefix}__parent__name', _PATH_SORT_EMPTY),
            _PATH_SORT_SEP,
            Coalesce(f'{relation_prefix}__name', _PATH_SORT_EMPTY),
            output_field=CharField(),
        ),
    })


@admin.register(Location)
class LocationAdmin(ModelAdmin):
    list_display = ['name', 'parent_path', 'user', 'created_at']
    list_filter = ['user', 'parent']
    search_fields = ['name']

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(*LOCATION_SELECT_RELATED)
        return annotate_fk_path_sort(qs, 'parent', 'parent_path_sort')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['form_class'] = LocationChoiceField
            kwargs['queryset'] = location_queryset()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Parent path', ordering='parent_path_sort')
    def parent_path(self, obj):
        return obj.parent


class PlantImageInline(TabularInline):
    model = PlantImage
    extra = 0
    readonly_fields = ['uploaded_at', 'taken_at']


class PlantCareLogInline(TabularInline):
    model = PlantCareLog
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Plant)
class PlantAdmin(ModelAdmin):
    list_filter_submit = True
    list_display = [
        'name', 'scientific_name', 'location_path', 'user',
        'last_watered', 'last_repotted', 'created_at',
    ]
    list_filter = [
        ('name', AllValuesCheckboxFilter),
        ('scientific_name', AllValuesCheckboxFilter),
        ('location', LocationDropdownFilter),
        ('user', UserDropdownFilter),
        LastWateredRangeFilter,
        LastRepottedRangeFilter,
        ('created_at', RangeDateFilter),
    ]
    search_fields = ['name', 'scientific_name']
    inlines = [PlantImageInline, PlantCareLogInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'location',
            'location__parent',
            'location__parent__parent',
            'location__parent__parent__parent',
        )
        last_watered = Subquery(
            PlantCareLog.objects.filter(plant=OuterRef('pk'), type='watered')
            .order_by('-logged_at').values('logged_at')[:1]
        )
        last_repotted = Subquery(
            PlantCareLog.objects.filter(plant=OuterRef('pk'), type='repotted')
            .order_by('-logged_at').values('logged_at')[:1]
        )
        return annotate_fk_path_sort(
            qs.annotate(last_watered=last_watered, last_repotted=last_repotted),
            'location',
            'location_path_sort',
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'location':
            kwargs['form_class'] = LocationChoiceField
            kwargs['queryset'] = location_queryset()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Location path', ordering='location_path_sort')
    def location_path(self, obj):
        return obj.location

    @admin.display(description='Last watered', ordering='last_watered')
    def last_watered(self, obj):
        return obj.last_watered

    @admin.display(description='Last repotted', ordering='last_repotted')
    def last_repotted(self, obj):
        return obj.last_repotted


@admin.register(PlantImage)
class PlantImageAdmin(ModelAdmin):
    list_display = ['id', 'plant', 'image_preview', 'caption', 'taken_at', 'uploaded_at']
    list_filter = [('plant__user', UserDropdownFilter), ('taken_at', RangeDateFilter), ('uploaded_at', RangeDateFilter)]
    search_fields = ['plant__name', 'caption']
    readonly_fields = ['image_preview', 'uploaded_at', 'taken_at']
    ordering = ['-taken_at']

    @admin.display(description='Preview')
    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;">', obj.image.url)
        return '—'


@admin.register(PlantCareLog)
class PlantCareLogAdmin(ModelAdmin):
    list_display = ['plant', 'type', 'logged_at']
    list_filter = ['type']
    search_fields = ['plant__name']
