from .forms import UpdateWizardForm2, UpdateWizardForm1

try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from .views import UpdateProjectFormView, UpdateFormView, UpdateUpdateView, UpdateDeleteView, UpdateDetailView, UpdateListView, UpdateWizardView, update_images

urlpatterns = patterns('updates',
                       url(r'^wizard/([\d-]+)/$', UpdateWizardView.as_view([UpdateWizardForm1, UpdateWizardForm2]), name='update-wizard'),
                       url(r'^create/([\d-]+)/$', UpdateProjectFormView.as_view(), name='update-project-form'),
                       url(r'^create/$', UpdateFormView.as_view(), name='update-form'),
                       url(r'^images/(?P<update_id>\d+)/$', update_images, name='update-images-formset'),
                       url(r'^update/(?P<pk>\d+)/$', UpdateUpdateView.as_view(), name='update-update'),
                       url(r'^delete/(?P<pk>\d+)/$', UpdateDeleteView.as_view(), name='update-delete'),
                       url(r'^(?P<pk>\d+)/$', UpdateDetailView.as_view(), name='update-detail'),
                       url(r'^$', UpdateListView.as_view(), name='update-list'),
)
