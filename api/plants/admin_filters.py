from collections.abc import Iterator

from django.contrib.admin.utils import EMPTY_VALUES
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from unfold.contrib.filters.admin import (
    AllValuesCheckboxFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.admin.datetime_filters import parse_date_str
from unfold.contrib.filters.forms import RangeDateForm

from .forms import location_queryset
from .models import Location


class LocationDropdownFilter(RelatedDropdownFilter):
    def field_choices(self, field, request, model_admin):
        qs = location_queryset(Location.objects.all())
        return [
            (location.pk, location.display_name)
            for location in sorted(qs, key=lambda loc: loc.path_names)
        ]

    def queryset(self, request, queryset):
        if self.value() in EMPTY_VALUES:
            return queryset
        location = Location.objects.get(pk=self.value())
        return queryset.filter(location_id__in=location.descendant_pks())


class UserDropdownFilter(RelatedDropdownFilter):
    def has_output(self):
        return len(self.lookup_choices) > 0


class AnnotatedDateRangeFilter(admin.SimpleListFilter):
    template = 'unfold/filters/filters_date_range.html'
    form_class = RangeDateForm

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.request = request
        for suffix in ('_from', '_to'):
            key = f'{self.parameter_name}{suffix}'
            if key in params:
                value = params.pop(key)
                value = value[0] if isinstance(value, list) else value
                if value:
                    self.used_parameters[key] = value

    def lookups(self, request, model_admin):
        return ()

    def queryset(self, request, queryset):
        filters = {}
        value_from = self.used_parameters.get(f'{self.parameter_name}_from')
        if value_from:
            filters[f'{self.parameter_name}__gte'] = parse_date_str(value_from)
        value_to = self.used_parameters.get(f'{self.parameter_name}_to')
        if value_to:
            filters[f'{self.parameter_name}__lte'] = parse_date_str(value_to)
        if not filters:
            return queryset
        try:
            return queryset.filter(**filters)
        except (ValueError, ValidationError):
            return queryset.none()

    def choices(self, changelist: ChangeList) -> Iterator[dict]:
        yield {
            'request': self.request,
            'parameter_name': self.parameter_name,
            'form': self.form_class(
                name=self.parameter_name,
                data={
                    f'{self.parameter_name}_from': self.used_parameters.get(
                        f'{self.parameter_name}_from'
                    ),
                    f'{self.parameter_name}_to': self.used_parameters.get(
                        f'{self.parameter_name}_to'
                    ),
                },
            ),
        }

    def expected_parameters(self):
        return [
            f'{self.parameter_name}_from',
            f'{self.parameter_name}_to',
        ]

    def has_output(self):
        return True


class LastWateredRangeFilter(AnnotatedDateRangeFilter):
    title = _('Last watered')
    parameter_name = 'last_watered'


class LastRepottedRangeFilter(AnnotatedDateRangeFilter):
    title = _('Last repotted')
    parameter_name = 'last_repotted'
