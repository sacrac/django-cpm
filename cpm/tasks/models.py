from django.db import models
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.timesince import timesince, timeuntil
from django.utils.translation import ugettext_lazy as _

from core.models import Slugged, base_concrete_model, DateStamp

from projects.models import Project


class Task(Slugged):
    project = models.ForeignKey(Project)
    category = models.ForeignKey('TaskCategory')
    projected_completion_date = models.DateField(_("Projected Completion Date"),
                                                 blank=True, null=True)
    completion_date = models.DateField(_("Actual Completion Date"),
                                       blank=True, null=True)
    description = models.TextField(blank=True)
    expense = models.IntegerField(blank=True)
    price = models.IntegerField(blank=True, verbose_name=_('Markup'))

    class Meta:
        order_with_respect_to = 'project'

    def get_absolute_url(self):
        return reverse('tasks:task-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('tasks:task-update', kwargs={'pk': self.pk})

    def due_date_until(self):
        if self.projected_completion_date:
            return timeuntil(self.projected_completion_date)

    def due_date_since(self):
        if self.projected_completion_date:
            return timesince(self.projected_completion_date)

    def get_status(self):
        if self.project.start_time:
            if self.completion_date:
                result = 2
            else:
                result = 1
        else:
            result = 0
        return result

    def get_project_category_totals(self):
        result_dict = {}
        all_categories = TaskCategory.objects.all()
        all_tasks = Task.objects.filter(project=self.project)
        all_categories = all_categories.order_by('order')
        print all_categories
        for cat in all_categories:
            cat_tasks = all_tasks.filter(category=cat)
            if cat_tasks:
                print cat.title
                cat_exp_total = sum(cat_tasks.values_list('expense', flat=True))
                cat_price_total = sum(cat_tasks.values_list('price', flat=True))
                result_dict[cat.slug] = {
                    'id': cat.id,
                    'title': cat.title,
                    'expense': cat_exp_total,
                    'price': cat_price_total,
                    'total': sum([cat_exp_total, cat_price_total]),
                    'tasks': cat_tasks
                }
        return result_dict

    due_date_since.short_description = _("Late by")
    due_date_until.short_description = _("Due in")


class TaskCategory(Slugged):
    parent = models.ForeignKey("TaskCategory", blank=True, null=True, related_name="children")
    ascendants = models.CharField(editable=False, max_length=1000, null=True)
    order = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('ascendants',)
        order_with_respect_to = 'parent'

    def save(self, *args, **kwargs):
        if self.order is None:
            if not TaskCategory.objects.all():
                self.order = 0
        ascendants = [str(self.id)]
        parent = self.parent
        while parent is not None:
            ascendants.insert(0, str(parent.id))
            parent = parent.parent
        self.ascendants = ",".join(ascendants)
        children = self.children.all()
        if children is not None:
            for child in children:
                super(TaskCategory, child).save(*args, **kwargs)

        super(TaskCategory, self).save(*args, **kwargs)

    def get_update_url(self):
        return reverse('tasks:task-category-update', kwargs={'pk': self.pk})

    def get_project_category_price(self, project):
        total = 0
        for p in project.task_set.filter(category=self):
            total += p.price
        return total

    def get_project_category_expense(self, project):
        total = 0
        for p in project.task_set.filter(category=self):
            total += p.expense
        return total


