import json
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.models import User

from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.forms.models import inlineformset_factory, modelformset_factory
from braces.views import JSONResponseMixin

from jsonview.decorators import json_view

from core.views import AjaxableResponseMixin

from projects.models import Project
from changes.models import ChangeOrder

from .models import Task, TaskCategory
from .forms import TaskForm, TaskCategoryForm

@json_view
def manage_tasks(request, project_id):
    project = Project.objects.get(pk=project_id)
    FormSet = inlineformset_factory(Project, Task, form=TaskForm)
    if request.method == 'POST':
        formset = FormSet(request.POST, request.FILES, instance=project)
        #TODO: There's no validation
        formset.save()
        return {'success': True}
    else:
        formset = render_crispy_form(FormSet())
    return {'formset': formset}



@json_view
def manage_categories(request):
    FormSet = modelformset_factory(TaskCategory, form=TaskCategoryForm)
    if request.method == 'POST':
        #TODO: There's no validation
        formset = FormSet(request.POST)
        print formset
        formset.save()
        for form in formset:
            print form.instance.id

        return {'success': True}
    else:
        formset = render_crispy_form(FormSet())
    return {'formset': formset}


class TaskListView(JSONResponseMixin, generic.ListView):
    #todo:This view needs to be redone. Using weird shit. Will keep for now for reference
    model = Task
    content_type = 'application/javascript'
    json_dumps_kwargs = {'indent': 2}
    template_name = 'tasks/task_list.html'

    def get(self, request, *arg, **kwargs):
        self.user = get_object_or_404(Project, id=self.args[0])
        project_tasks = Task.objects.filter(project=self.user)
        if request.is_ajax():
            context = {}
            for task in project_tasks:
                task_context = {
                    'title': task.title,
                    'description': task.description,
                    'project': task.project.title,
                    'status': task.get_status(),
                    'projected_completion_date': task.projected_completion_date
                }
                context[task.id] = task_context

            context.update(kwargs)
            return self.render_json_response(context)
        else:
            context = {'task_list': project_tasks}
            return render(request, self.template_name, context)


class TaskDetailView(JSONResponseMixin, generic.DetailView):
    model = Task
    content_type = 'application/javascript'
    json_dumps_kwargs = {'indent': 2}
    template_name = 'tasks/task_detail.html'

    def get(self, request, *arg, **kwargs):
        if request.is_ajax():
            context = {}
            context.update(kwargs)

            context += {
                'title': self.object.title,
                'description': self.object.description,
                'project': self.object.project.title,
                'status': self.object.status,
                'projected_completion_date': self.object.projected_completion_date
            }

            return self.render_json_response(context)
        else:
            context = {'task': self.get_object(self.get_queryset())}
            return render(request, self.template_name, context)


class TaskListUpdateView(generic.ListView):
    model = Task
    template_name = 'tasks/task_update_json.html'


class TaskFormView(generic.CreateView):
    model = Task
    form_class = TaskForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskFormView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            if request.POST['changes']:
                changes = request.POST['changes']
                print 'CHANGES:  ' + changes
            else:
                changes = ''
            return self.form_valid(form, changes)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, changes):
        new_task = form.save(commit=False)
        new_task.save()
        if changes:
            new_task.changes.add(changes)
            print(new_task.changes.all())
        else:
            print 'NO CHANGE ORDER'
        update_url = form.instance.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'new': True}
        return context

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        form_html = render_crispy_form(self.form_class())
        context = {'form_html': form_html}
        return context


class TaskUpdateView(generic.UpdateView):
    model = Task
    form_class = TaskForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        update_url = self.object.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'new': False}
        return context

    def form_invalid(self, form):
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        self.object = super(TaskUpdateView, self).get_object()
        form = self.form_class(instance=self.object)
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        context = {'form_html': form_html}
        return context


class TaskDeleteView(generic.DeleteView):
    model = Task

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        context = {'success': True}
        return context

    def form_invalid(self, form):
        return {'success': False}

class TaskCategoryListView(generic.ListView):
    model = TaskCategory

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskCategoryListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.queryset = super(TaskCategoryListView, self).get_queryset()
        context = {}
        for cat in self.get_queryset():
            context[cat.id] = {
                'id': cat.id,
                'title': cat.title,
                'title_url': urlquote(cat.title),
                'update_url': cat.get_update_url(),
                'description': cat.description,
                'order': cat.order,
            }

        return context


def tree_branch(branch):
    return {
        'id': branch.id,
        'parent': branch.parent_id,
        'ascendants': branch.ascendants,
        'title': branch.title,
        'title_url': urlquote(branch.title),
        'update_url': branch.get_update_url(),
        'description': branch.description,
        'order': branch.order,
        '_order': branch._order,
        'children': []
    }


def get_r_branch(tree):
    branch = tree_branch(tree)
    if tree.children.all():
        for child in tree.children.all():
            branch['children'].append(
                get_r_branch(child)
            )
    return branch


class TaskCategoryListViewAlt(TaskCategoryListView):

    def get_queryset(self):
        self.primary_categories = TaskCategory.objects.filter(parent=None)
        return self.primary_categories

    def get(self, request, *args, **kwargs):
        self.queryset = super(TaskCategoryListViewAlt, self).get_queryset()
        context = {'category_list': []}
        for cat in self.get_queryset():
            context['category_list'].append(get_r_branch(cat))
        return context


@json_view
def task_category_json(request, pk):
    category = get_object_or_404(TaskCategory, id=pk)
    context = {
        'id': category.id,
        'title': category.title,
        'title_url': urlquote(category.title),
        'slug': category.slug,
        'description': category.description,
        'update_url': category.get_update_url(),
    }

    return context


class TaskCategoryFormView(generic.CreateView):
    model = TaskCategory
    form_class = TaskCategoryForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskCategoryFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        print form
        form.save()
        update_url = form.instance.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'new': True,
                   'pk': form.instance.id}
        return context

    def form_invalid(self, form):
        print form
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        form_html = render_crispy_form(self.form_class())
        context = {'form_html': form_html}
        return context


class TaskCategoryUpdateView(generic.UpdateView):
    model = TaskCategory
    form_class = TaskCategoryForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskCategoryUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        update_url = self.object.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'new': False}
        return context

    def form_invalid(self, form):
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        self.object = super(TaskCategoryUpdateView, self).get_object()
        form = self.form_class(instance=self.object)
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        context = {'form_html': form_html}
        return context


class TaskCategoryDeleteView(generic.DeleteView):
    model = TaskCategory
    success_url = reverse_lazy('tasks:task-list')
