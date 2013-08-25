try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from .views import TaskFormView, TaskUpdateView, TaskDeleteView, TaskListView, TaskDetailView, manage_tasks, \
    TaskListUpdateView, TaskCategoryDeleteView, TaskCategoryUpdateView, TaskCategoryFormView, manage_categories, \
    task_category_json, TaskCategoryListView, TaskCategoryListViewAlt, CategoryBundleView, CategoryBundleListView, \
    CategoryBundleFormView, CategoryBundleUpdateView, CategoryBundleDeleteView


urlpatterns = patterns('tasks',
                       url(r'^category/bundle/update/(?P<pk>\d+)/$', CategoryBundleUpdateView.as_view(),
                           name='bundle-update'),
                       url(r'^category/bundle/create/$', CategoryBundleFormView.as_view(), name='bundle-form'),
                       url(r'^category/bundle/delete/(?P<pk>\d+)/$', CategoryBundleDeleteView.as_view(),
                           name='bundle-delete'),
                       url(r'^category/bundle/(?P<pk>\d+)/$', CategoryBundleView.as_view(), name='category-bundle'),
                       url(r'^category/bundle/$', CategoryBundleListView.as_view(), name='bundle-list'),
                       url(r'^category/create/$', TaskCategoryFormView.as_view(), name='task-category-form'),
                       url(r'^category/update/(?P<pk>\d+)/$', TaskCategoryUpdateView.as_view(),
                           name='task-category-update'),
                       url(r'^category/delete/(?P<pk>\d+)/$', TaskCategoryDeleteView.as_view(),
                           name='task-category-delete'),
                       url(r'^category/manage/$', manage_categories, name='category-manager'),
                       url(r'^category/json/(?P<pk>\d+)/$',
                           task_category_json, name='task-category-detail-json'),
                       url(r'^category/alt/$', TaskCategoryListViewAlt.as_view(),
                           name='task-category-list-alt'),
                       url(r'^category/$', TaskCategoryListView.as_view(),
                           name='task-category-list'),
                       url(r'^create/$', TaskFormView.as_view(), name='task-form'),
                       url(r'^manage/(?P<project_id>\d+)/$', manage_tasks, name='task-manager'),
                       url(r'^update/(?P<pk>\d+)/$', TaskUpdateView.as_view(), name='task-update'),
                       url(r'^delete/(?P<pk>\d+)/$', TaskDeleteView.as_view(), name='task-delete'),
                       url(r'^project/([\d-]+)/$', TaskListView.as_view(), name='task-list'),
                       url(r'^(?P<pk>\d+)/$', TaskDetailView.as_view(), name='task-detail'),
                       url(r'^$', TaskListUpdateView.as_view(), name='task-list-update'),
)

