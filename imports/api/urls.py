from django.urls import re_path

from imports.api.views import (CreateDataSetView, UpdateCitizenView, ListDataSetCitizensView,
                               DataSetBirthdaysView, DataSetAgePercentiles, )

urlpatterns = [
    re_path(r'^imports/?$',
            CreateDataSetView.as_view(),
            name='create_dataset'),
    re_path(r'^imports/(?P<data_set_id>\d+)/citizens/?$',
            ListDataSetCitizensView.as_view(),
            name='list_citizens'),
    re_path(r'^imports/(?P<data_set_id>\d+)/citizens/(?P<citizen_id>\d+)/?$',
            UpdateCitizenView.as_view(),
            name='update_citizen'),
    re_path(r'^imports/(?P<data_set_id>\d+)/citizens/birthdays/?$',
            DataSetBirthdaysView.as_view(),
            name='get_birthdays'),
    re_path(r'^imports/(?P<data_set_id>\d+)/towns/stat/percentile/age/?$',
            DataSetAgePercentiles.as_view(),
            name='get_age_percentiles'),
]
