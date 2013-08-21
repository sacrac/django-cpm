from django.db import models
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.timesince import timesince, timeuntil
from django.utils.translation import ugettext_lazy as _

from core.models import Slugged, base_concrete_model, DateStamp

from projects.models import Project
import reversion


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
        for cat in all_categories:
            cat_tasks = all_tasks.filter(category=cat)
            if cat_tasks:
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
reversion.register(Task)


class TaskCategory(Slugged):
    parent = models.ForeignKey("TaskCategory", blank=True, null=True,
                               related_name="children")
    ascendants = models.CharField(editable=False, max_length=100, null=True)
    order = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('_order', 'order', 'ascendants')
        order_with_respect_to = 'parent'

    def save(self, *args, **kwargs):

        if self.parent is None:
            self._order = self.order

        if self.ascendants:
            if not self.id in [int(ascendant) for ascendant in self.ascendants.split(',')[:-1]]:
                if self.update_descendants():
                    super(TaskCategory, self).save(*args, **kwargs)
            else:
                print 'error: self id in ascendants'
        else:
            super(TaskCategory, self).save(*args, **kwargs)
            self.update_descendants()

    def update_descendants(self):
        current_ascendants = self.ascendants
        print 'current: ' + str(current_ascendants)

        ascendants = [str(self.id)]
        parent = self.parent
        while parent is not None and parent is not self:
            ascendants.insert(0, str(parent.id))
            if parent.parent:
                parent = parent.parent
            else:
                #the while condition will set parent to None and we cant validate it so we end the loop before this
                #while the parent is not None
                break
            if parent == self:
                break

        if parent != self or parent is None:
            print 'parent safe'
            ascendants = ",".join(ascendants)
            self.ascendants = ascendants

            if ascendants != current_ascendants or ascendants is None:
                super(TaskCategory, self).save(update_fields=['ascendants'])
                print 'new    : ' + str(self.ascendants)

            children = self.children.all()
            if children:
                for child in children:
                    child.update_descendants()
            return True
        else:
            return False


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


