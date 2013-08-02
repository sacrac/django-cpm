from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote

from string import punctuation
from urllib import unquote

from core.utils import import_dotted_path
from core.models import Slugged, base_concrete_model, DateStamp


class Project(DateStamp, Slugged):
    user = models.ForeignKey(User, blank=True)
    description = models.TextField(blank=True)
    completion = models.IntegerField(default=0)
    start_time = models.DateField(blank=True, null=True)

    #blueprints
    #drawings

    def get_absolute_url(self):
        return reverse('projects:project-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('projects:project-update', kwargs={'pk': self.pk})

    def get_progress(self):
        task_set = self.task_set.all()
        task_count = float(task_set.count())
        com_tasks = task_set.filter(completion_date__isnull=False)
        result = 0
        if com_tasks:
            result = (com_tasks.count() / task_count)
        return result

    def get_category_price(self, category):
        total = 0
        for p in self.task_set.filter(category=category):
            total += p.price
        return total

    def get_category_expense(self, category):
        total = 0
        for p in self.task_set.filter(category=category):
            total += p.expense
        return total

    def get_category_total(self, category):
        return sum(self.get_category_expense(category), self.get_category_price(category))

    def get_project_price(self):
        total = 0
        for p in self.task_set.all():
            total += p.price
        return total

    def get_project_expense(self):
        total = 0
        for p in self.task_set.all():
            total += p.expense
        return total

    def get_project_total(self):
        total = 0
        for p in self.task_set.all():
            total += p.price
            total += p.expense
        return total

    def get_project_category_totals(self):
        result_dict = {}
        cat_dict = {}
        all_tasks = self.task_set.all()
        for task in all_tasks:
            try:
                cat_dict[task.category.id]
            except KeyError:
                cat_dict[task.category.id] = task.category
        for cat in cat_dict:
            cat_exp_total = self.get_category_expense(cat_dict[cat])
            cat_price_total = self.get_category_price(cat_dict[cat])
            task_set_objects = all_tasks.filter(category_id=cat_dict[cat].id)
            task_set = task_set_objects.values()
            task_set_json = {}
            for task in task_set:
                task['title_url'] = urlquote(task['title'])
                task['update_url'] = task_set_objects.get(id=task['id']).get_update_url()
                if task['completion_date']:
                    task['completion_date'] = task['completion_date'].toordinal()
                if task['projected_completion_date']:
                    task['projected_completion_date'] = task['projected_completion_date'].toordinal()
                task_set_json[task['id']] = task
            result_dict[cat_dict[cat].id] = {
                'id': cat_dict[cat].id,
                'slug': cat_dict[cat].slug,
                'title': cat_dict[cat].title,
                'title_url': urlquote(cat_dict[cat].title),
                'order': cat_dict[cat].order,
                'expense': cat_exp_total,
                'price': cat_price_total,
                'total': sum([cat_exp_total, cat_price_total]),
                'task_set': task_set_json,
            }
        return result_dict


class ProjectImage(Slugged):
    project = models.ForeignKey(Project, related_name="project_images")
    image = models.ImageField(max_length=200, upload_to='projects')

    class Meta:
        verbose_name = _("Project Image")
        verbose_name_plural = _("Project Images")
        order_with_respect_to = 'project'

