from django.db import models
from django.core.urlresolvers import reverse

from core.models import Slugged, base_concrete_model, DateStamp

from projects.models import Project
from tasks.models import Task


#TODO:Add field for client to accept change order
class ChangeOrder(DateStamp, Slugged):
    project = models.ForeignKey(Project)
    description = models.TextField(blank=True)
    tasks = models.ManyToManyField(Task, blank=True, related_name='changes')

    def get_absolute_url(self):
        return reverse('changes:change-detail', kwargs={'pk': self.pk})


