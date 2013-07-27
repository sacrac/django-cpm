try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from .views import ChangeOrderProjectFormView, ChangeOrderFormView, ChangeOrderUpdateView, ChangeOrderDeleteView, ChangeOrderDetailView, ChangeOrderListView, change_order_tasks_json

urlpatterns = patterns('changes',
                       url(r'^tasks/json/(?P<pk>\d+)/$', change_order_tasks_json, name='change-tasks-json'),
                       url(r'^create/([\d-]+)/$', ChangeOrderProjectFormView.as_view(), name='change-user-form'),
                       url(r'^create/$', ChangeOrderFormView.as_view(), name='change-form'),
                       url(r'^update/(?P<pk>\d+)/$', ChangeOrderUpdateView.as_view(), name='change-change'),
                       url(r'^delete/(?P<pk>\d+)/$', ChangeOrderDeleteView.as_view(), name='change-delete'),
                       url(r'^(?P<pk>\d+)/$', ChangeOrderDetailView.as_view(), name='change-detail'),
                       url(r'^$', ChangeOrderListView.as_view(), name='change-list'),
                       )
