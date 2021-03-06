from string import punctuation
from urllib import unquote
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from core.models import Slugged, base_concrete_model, DateStamp

from projects.models import Project
from tasks.models import Task


class Update(DateStamp, Slugged):
    project = models.ForeignKey(Project)
    description = models.TextField(blank=True)
    tasks = models.ManyToManyField(Task, blank=True)

    def get_absolute_url(self):
        return reverse('updates:update-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('updates:update-update', kwargs={'pk': self.pk})

    def add_tasks(self):
        if self.tasks:
            for task in self.tasks.all():
                task.completion_date = now().date()
                task.save()

    def project_images(self):
        return self.project.project_images.filter(update=self)

    def get_task_choices(self):
        if self.project:
            choices = [(task.id, task.title) for task in self.project.task_set.all()]
        else:
            choices = []
        return choices



class UpdateImage(Slugged):
    #TODO: REMOVE THIS
    update = models.ForeignKey(Update, related_name="update_images")
    image = models.ImageField(max_length=200, upload_to='updates')

    class Meta:
        verbose_name = _("Update Image")
        verbose_name_plural = _("Update Images")
        order_with_respect_to = 'update'

