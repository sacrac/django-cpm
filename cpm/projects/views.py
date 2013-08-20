from calendar import month_name
import json, urllib
from crispy_forms.utils import render_crispy_form
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.extras.widgets import SelectDateWidget
from django.forms.models import inlineformset_factory

from django.utils.http import urlquote
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import RedirectView

import reversion
from reversion.helpers import generate_patch_html

from core.views import AjaxableResponseMixin
from tasks.models import TaskCategory
from tasks.forms import TaskForm, TaskCategoryForm
from jsonview.decorators import json_view

from .forms import ProjectForm, ProjectFilterForm
from .models import Project, ProjectImage
from .helpers import create_project_summary_tree



def get_dict_in_list_2(key, key0, value, value0, dict_list):
    """
    looks through a list of dictionaries and returns dict, where dict[key] == value
    """
    result = None
    for dict in dict_list:
        if dict[key] == value:
            if dict[key0] == value0:
                result = dict
    return result

@json_view
def version_diff(request, pk, old_pk):
    revision = get_object_or_404(reversion.models.Revision, pk=pk)
    old_revision = get_object_or_404(reversion.models.Revision, pk=old_pk)
    version_set = []
    old_version_set = []
    for v in revision.version_set.all():
        version = {'type': v.content_type.name, 'id': v.object_id_int, 'version': v}
        version_set.append(version)
    for v in old_revision.version_set.all():
        version = {'type': v.content_type.name, 'id': v.object_id_int, 'version': v}
        old_version_set.append(version)
    context = []
    for version in version_set:
        old_version = get_dict_in_list_2('id', 'type', version['id'], version['type'], old_version_set)
        if old_version:
            patches = []
            for field in version['version'].field_dict:
                patch = generate_patch_html(old_version['version'], version['version'], field, cleanup='semantic')
                patches.append({'field': field, 'patch': patch})
            context.append({
                'pk': version['id'],
                'model': version['type'],
                'patches': patches
            })

    return context

def version_compare(request, pk, old_pk):
    revision = get_object_or_404(reversion.models.Revision, pk=pk)
    old_revision = get_object_or_404(reversion.models.Revision, pk=old_pk)
    context = {'old_revision': old_revision, 'revision': revision}
    return render(request, 'reversion/revision_detail.html', context)


class VersionDetailView(generic.DetailView):
    model = reversion.models.Revision

class VersionDetailJSONView(generic.DetailView):
    model = reversion.models.Revision

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(VersionDetailJSONView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = super(VersionDetailJSONView, self).get_object()
        context = [version.serialized_data for version in self.object.version_set.all()]

        return context

@json_view
def project_proposal(request, project_id):
    project_summary = create_project_summary_tree(project_id=project_id)

    return {'project_summary': project_summary}


class ProjectDetailJSONView(generic.DetailView):
    model = Project

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(ProjectDetailJSONView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = super(ProjectDetailJSONView, self).get_object()
        version_list = reversion.get_for_object(self.object)[:10]
        versions = []
        for version in version_list:
            #instance_data = version.serialized_data.strip('[]')
            timestamp = str(version.revision.date_created.isoformat()[:-13])
            versions.append({
                'version': version.pk,
                'created': timestamp
            })

        context = {
            'id': self.object.id,
            'title': self.object.title,
            'title_url': urlquote(self.object.title),
            'slug': self.object.slug,
            'user': self.object.user.id,
            'username': self.object.user.username,
            'description': self.object.description,
            'completion': self.object.completion,
            'created': self.object.created.toordinal(),
            'modified': self.object.modified.toordinal(),
            'absolute_url': self.object.get_absolute_url(),
            'update_url': self.object.get_update_url(),
            'category_totals': self.object.get_project_category_totals(),
            'versions': versions,
            'price': self.object.get_project_price(),
            'expense': self.object.get_project_expense(),
            'total': self.object.get_project_total()

        }

        return context


class ProjectDetailView(generic.DetailView):
    model = Project


def project_list_super(request, user=None, year=None, month=None):
    user_list = User.objects.filter(is_staff=False)
    project_select_form = ProjectFilterForm()
    project_list = Project.objects.all()
    if user is not None:
        user = get_object_or_404(User, id=user)
        project_list = project_list.filter(user=user)
        user = user

    if year is not None:
        project_list = project_list.filter(created__year=year)
        if month is not None:
            project_list = project_list.filter(created__month=month)
            month = month_name[int(month)]

    context = {
        "project_list": project_list, "year": year, "month": month,
        "project_select_form": project_select_form,
        "user_list": user_list, "project_user": user
    }

    return render(request, "projects/project_list_super.html", context)


class ProjectListView(generic.ListView):
    model = Project

    def get_queryset(self):
        self.user = get_object_or_404(User, id=self.args[0])
        return Project.objects.filter(user=self.user)

    def get_context_data(self, **kwargs):
        self.queryset = super(ProjectListView, self).get_queryset()
        #TODO: I think this is redundant remove if there arent any errors
        #self.user = get_object_or_404(User, id=self.args[0])
        context = {
            'client': self.user
        }
        context.update(kwargs)
        return super(ProjectListView, self).get_context_data(**context)


class ProjectWizardView(AjaxableResponseMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def get_context_data(self, **kwargs):
        context = {
            'task_form': TaskForm(),
            'task_category_form': TaskCategoryForm(),
            'task_categories': TaskCategory.objects.all().order_by('order')
        }
        context.update(kwargs)
        return super(ProjectWizardView, self).get_context_data(**context)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            update_url = self.object.get_update_url()
            data = {
                'success': True,
                'pk': self.object.pk,
                'update_url': update_url,
            }
            return self.render_to_json_response(data)
        else:
            return response


class ProjectFormView(generic.CreateView):
    model = Project
    form_class = ProjectForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(ProjectFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        with reversion.create_revision():
            form.save()
        update_url = form.instance.get_update_url()
        form_html = render_crispy_form(form)
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'pk': form.instance.id}
        return context

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        form = ProjectForm()
        form_html = render_crispy_form(form)
        context = {'form_html': form_html}
        return context


class ProjectUpdateView(generic.UpdateView):
    model = Project
    form_class = ProjectForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        with reversion.create_revision():
            form.save()
            reversion.set_user(form.instance.user)
            print(form.instance.user)
            print(reversion.get_user())
        form_html = render_crispy_form(form)
        update_url = form.instance.get_update_url()
        context = {'success': True, 'form_html': form_html, 'pk': form.instance.id, 'update_url': update_url}
        return context

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        object = super(ProjectUpdateView, self).get_object()
        form_html = render_crispy_form(ProjectForm(instance=object))
        context = {'form_html': form_html}
        return context


class ProjectRedirectView(RedirectView):
    """
    redirects users to their project view
    """
    permanent = False
    query_string = True

    def get_redirect_url(self, **kwargs):
        if not self.request.user.is_authenticated():
            return reverse('login')
        else:
            return reverse('projects:project-list', args=(self.request.user.id,))


class ProjectDeleteView(generic.DeleteView):
    model = Project
    success_url = reverse_lazy('projects:project-list-super')


@json_view
def set_task_order(request, pk):
    project = get_object_or_404(Project, id=pk)

    if request.method == 'POST':
        task_order = request.POST['task_order'].split(',')
        print task_order
        project.set_task_order(task_order)
        project.save()
        return {'task_order': project.get_task_order(), 'success': True}
    else:
        return {'task_order': project.get_task_order(), 'success': False}


def project_images(request, project_id):
    project = Project.objects.get(pk=project_id)
    FormSet = inlineformset_factory(Project, ProjectImage)
    formset = FormSet(instance=project)
    if request.method == 'POST':
        formset = FormSet(request.POST, request.FILES, instance=project)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse_lazy('projects:project-list-super'))

    return render(request, 'projects/project_images.html', {'formset': formset, 'project': project})


'''
def project_redirect(request):
    return redirect(ProjectListView.as_view(), args=(request.user.id,))
def manage_tasks(request, project_id):
    project = Project.objects.get(pk=project_id)
    ProjectFormSet = inlineformset_factory(Project, Project, form=ProjectForm)
    if request.method == 'POST':
        formset = ProjectFormSet(request.POST, request.FILES, instance=project)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        formset = ProjectFormSet(instance=project)
    return render_to_response('projects/manage_projects.html', {'formset': formset, 'project': project})
'''

