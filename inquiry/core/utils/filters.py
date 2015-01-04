'''
Created on Jan 3, 2015

@author: briansoby
'''
import json
from django_filters import FilterSet, MethodFilter

class BaseFilterSet(FilterSet):
    pk__in = MethodFilter(action="handle_pk_in")
    
    def handle_pk_in(self, queryset, value):
        l = json.loads(value)
        if l:
            return queryset.filter(id__in=l)
        return queryset