from django.conf import settings
from django.conf.urls.static import static

try:
    from django.conf.urls import *
except ImportError:  # django < 1.4
    from django.conf.urls.defaults import *

from django.contrib import admin
from projects.views import ProjectRedirectView

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^cpm/updates/', include('updates.urls', namespace='updates')),
                       url(r'^cpm/changes/', include('changes.urls', namespace='changes')),
                       url(r'^cpm/tasks/', include('tasks.urls', namespace='tasks')),
                       url(r'^cpm/', include('projects.urls', namespace='projects')),
                       url(r'^messages/', include('messages.urls', namespace='messages')),
                       #url(r'^timelines/$', include('timelines.urls', namespace='timelines')),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='login'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
                       url(r'^accounts/', include('accounts.urls', namespace='accounts')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', ProjectRedirectView.as_view())
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
