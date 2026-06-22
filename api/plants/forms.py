from django import forms
from django.forms.models import ModelChoiceIterator

from .models import Location

LOCATION_SELECT_RELATED = (
    'parent',
    'parent__parent',
    'parent__parent__parent',
)


def location_queryset(queryset=None):
    qs = queryset if queryset is not None else Location.objects.all()
    return qs.select_related(*LOCATION_SELECT_RELATED)


class LocationChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        if queryset is None:
            return
        for obj in sorted(queryset, key=lambda loc: loc.path_names):
            yield self.choice(obj)


class LocationChoiceField(forms.ModelChoiceField):
    iterator = LocationChoiceIterator

    def label_from_instance(self, obj):
        return obj.display_name
