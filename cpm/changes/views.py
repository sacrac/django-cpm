from crispy_forms.utils import render_crispy_form
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django import forms

from projects.models import Project
from jsonview.decorators import json_view

from .models import ChangeOrder


@json_view
def change_order_tasks_json(request, pk):
    co = get_object_or_404(ChangeOrder, id=pk)
    tasks = co.tasks.all()
    context = {}
    for task in tasks:
        context[task.id] = {
            'id': task.id,
            'title': task.title,
            'update_url': task.get_update_url()
        }
    return context


class ChangeOrderListView(generic.ListView):
    model = ChangeOrder


class ChangeOrderDetailView(generic.DetailView):
    model = ChangeOrder


class ChangeOrderFormView(generic.CreateView):
    model = ChangeOrder


class ChangeOrderProjectFormView(generic.CreateView):
    model = ChangeOrder

    def form_valid(self, form):
        form.instance.project = get_object_or_404(Project, id=self.args[0])
        form.save()
        redirect_url = reverse_lazy('projects:project-wizard') + '?project=%d&change_order=%d' % \
                       (form.instance.project_id, form.instance.id)
        return HttpResponseRedirect(redirect_url)


class ChangeOrderUpdateView(generic.UpdateView):
    model = ChangeOrder


class ChangeOrderApprovalForm(forms.ModelForm):
    class Meta:
        model = ChangeOrder
        exclude = ('project', 'description', 'tasks', 'title', 'slug', )


class ChangeOrderUpdateView(generic.UpdateView):
    model = ChangeOrder
    form_class = ChangeOrderApprovalForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(ChangeOrderUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        update_url = self.object.get_update_url()
        #if form['approved'] == 0:
        print form
        context = {'success': True, 'update_url': update_url}
        return context

    def form_invalid(self, form):
        return {'success': False}


class ChangeOrderDeleteView(generic.DeleteView):
    model = ChangeOrder
    success_url = reverse_lazy('changes:change-list')
