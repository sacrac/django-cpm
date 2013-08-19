try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from .views import ProjectWizardView, ProjectFormView, ProjectUpdateView, ProjectDeleteView, ProjectDetailView, \
    ProjectDetailJSONView, ProjectListView, ProjectRedirectView, set_task_order, project_list_super, project_images, project_proposal, VersionDetailView

urlpatterns = patterns('projects',
                       url(r'^wizard/$', ProjectWizardView.as_view(), name='project-wizard'),
                       url(r'^create/$', ProjectFormView.as_view(), name='project-form'),
                       #url(r'^manage/(?P<project_id>\d+)/$', manage_projects, name='project-manager'),
                       url(r'^update/(?P<pk>\d+)/$', ProjectUpdateView.as_view(), name='project-update'),
                       url(r'^delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),
                       #url(r'^users/([\d-]+)/$', ProjectUserListView.as_view(), name='project-user-list'),
                       url(r'^images/(?P<project_id>\d+)/$', project_images, name='project-images-formset'),
                       url(r'^projects/json/(?P<pk>\d+)/$', ProjectDetailJSONView.as_view(), name='project-detail-json'),
                       url(r'^projects/summary/json/(?P<project_id>\d+)/$', project_proposal, name='project-proposal-json'),
                       url(r'^projects/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
                       url(r'^projects/set_task_order/(?P<pk>\d+)/$', set_task_order, name='set-task-order'),
                       url("^list/user/(?P<user>\d+)/$", project_list_super, name='project-list-super-user'),
                       url("^list/month/(?P<year>\d{4})/(?P<month>\d{1,2})/$", project_list_super,
                           name='project-list-super-month'),
                       url("^list/year/(?P<year>\d{4})/$", project_list_super, name='project-list-super-year'),
                       url(r'^list/$', project_list_super, name='project-list-super'),
                       url(r'^versions/(?P<pk>\d+)/$', VersionDetailView.as_view(), name='version-detail'),
                       url(r'^([\d-]+)/$', ProjectListView.as_view(), name='project-list'),
                       url(r'^$', ProjectRedirectView.as_view(), name='project-redirect'),
)
