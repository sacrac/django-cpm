from crispy_forms.utils import render_crispy_form
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, render
from django.utils.timezone import now
from django.views import generic
from django.core.urlresolvers import reverse_lazy

from projects.models import Project
from tasks.models import Task
from jsonview.decorators import json_view
import reversion

from .models import Update, UpdateImage
from .forms import UpdateWizardForm1, UpdateWizardForm2, UpdateForm

from django.contrib.formtools.wizard.views import SessionWizardView


class UpdateWizardView(SessionWizardView):
    #def get_template_names(self):

    def get_form_step_data(self, form):
        self.project = get_object_or_404(Project, id=self.args[0])
        form.instance.project = self.project
        return form.data

    def done(self, form_list, **kwargs):
        for form in form_list:
            print form

            form.save()
        return HttpResponseRedirect(reverse_lazy('projects:project-list'))


class UpdateListView(generic.ListView):
    model = Update


class UpdateDetailView(generic.DetailView):
    model = Update

'''
class UpdateFormView(generic.CreateView):
    model = Update
    template_name = 'updates/update_form.html'

    def form_valid(self, form):
        form.save()
        if form.instance.tasks:
            for task in form.instance.tasks.all():
                task.completion_date = now().date()
                task.save()
        project = Project.objects.get(id=form.instance.project_id)
        print project.id
        with reversion.create_revision():
            project.save()
            reversion.set_comment('Pre Update: ' + form.instance.title)
        return HttpResponseRedirect(reverse_lazy('updates:update-images-formset', kwargs={'update_id': form.instance.id}))
'''

class UpdateFormView(generic.CreateView):
    model = Update
    form_class = UpdateForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(UpdateFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        project = get_object_or_404(Project, id=form.instance.project_id)
        print project.id
        with reversion.create_revision():
            project.save()
            reversion.set_comment('Pre Update: ' + form.instance.title)
        if form.instance.tasks:
            for task in form.instance.tasks.all():
                task.completion_date = now().date()
                task.save()
        form_html = render_crispy_form(form)
        update_url = form.instance.get_update_url()
        context = {'success': True, 'form_html': form_html, 'pk': form.instance.id, 'update_url': update_url}
        #return HttpResponseRedirect(reverse_lazy('updates:update-images-formset', kwargs={'update_id': form.instance.id}))
        return context

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form_html = render_crispy_form(form)
        context = {'form_html': form_html}
        return context


class UpdateUpdateView(generic.UpdateView):
    model = Update


class UpdateDeleteView(generic.DeleteView):
    model = Update
    success_url = reverse_lazy('updates:update-list')


def update_images(request, update_id):
    update = Update.objects.get(pk=update_id)
    FormSet = inlineformset_factory(Update, UpdateImage)
    formset = FormSet(instance=update)
    if request.method == 'POST':
        formset = FormSet(request.POST, request.FILES, instance=update)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse_lazy('updates:update-list'))

    return render(request, 'updates/update_images.html', {'formset': formset, 'update': update})
