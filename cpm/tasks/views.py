import json
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.models import User
from django.db.models import Q

from django.shortcuts import render_to_response, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.http import urlquote
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.forms.models import inlineformset_factory, modelformset_factory

from braces.views import JSONResponseMixin

from jsonview.decorators import json_view

from core.views import AjaxableResponseMixin

from projects.models import Project
from changes.models import ChangeOrder
from projects.helpers import unique_items

from .models import Task, TaskCategory, CategoryBundle
from .forms import TaskForm, TaskCategoryForm, CategoryBundleForm


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
    return {'formset': formset, 'success': False}


@json_view
def manage_categories(request):
    FormSet = modelformset_factory(TaskCategory, form=TaskCategoryForm)
    if request.method == 'POST':
        formset = FormSet(request.POST)
        if formset.is_valid():
            formset.save()
            for form in formset:
                cat = TaskCategory.objects.get(id=form.instance.id)
                all_cats = cat.children.all()
                if all_cats:
                    ordered_cats = []
                    for child in all_cats.order_by('order'):
                        ordered_cats.append(child.id)
                    cat.set_taskcategory_order(ordered_cats)
            return {'success': True}
        else:
            print formset.errors
            formset = render_crispy_form(formset)
    else:
        formset = render_crispy_form(FormSet())
    return {'formset': formset, 'success': False}


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
            print 'CHANGE ORDER INCLUDED'
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

    def post(self, request, *args, **kwargs):
        changes = None
        if "changes" in request.POST:
            changes = request.POST['changes']
            print changes
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form, changes)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, changes):
        #TODO: Form processing needed
        form.save()
        if changes:
            self.object.changes.add(changes)
            self.object.save()
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
    success_url = reverse_lazy('tasks:task-form')

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

    def delete(self, request, *args, **kwargs):
        self.object = super(TaskDeleteView, self).get_object()
        self.object.delete()
        return {'success':True}


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
                'parent': cat.parent_id,
                'ascendants': cat.ascendants
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
        for child in tree.children.all().order_by('_order'):
            branch['children'].append(
                get_r_branch(child)
            )
    return branch


class TaskCategoryListViewAlt(TaskCategoryListView):
    queryset = TaskCategory.objects.filter(parent=None).order_by("_order")

    def get(self, request, *args, **kwargs):
        self.queryset = super(TaskCategoryListViewAlt, self).get_queryset()
        context = {'category_list': []}
        for cat in self.get_queryset():
            context['category_list'].append(get_r_branch(cat))
        return context


def category_tree_list():
    primary_cats = TaskCategory.objects.filter(parent=None).order_by("_order")
    cat_list = {'category_list': []}
    for cat in primary_cats:
        cat_list['category_list'].append(get_r_branch(cat))
    return cat_list


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
        form.save()
        update_url = form.instance.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html, 'new': True,
                   'pk': form.instance.id}
        return context

    def form_invalid(self, form):
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
    success_url = reverse_lazy('tasks:task-category-list')

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(TaskCategoryDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        return {'success': True}

    def form_invalid(self, form):
        print form
        return {'success': False}

    def delete(self, request, *args, **kwargs):
        self.object = super(TaskCategoryDeleteView, self).get_object()
        self.object.delete()
        return {'success':True}

def get_descendant_ids(branch):
    children = branch.children.all()
    child_ids = [branch.id]
    if children:
        for child in children:
            child_ids.extend(get_descendant_ids(child))
    return child_ids

def remove_duplicate_ids(id_array):
    ids_to_remove = []
    for id_set in id_array:
        for id_set2 in id_array:
            if id_set[0] in id_set2 and id_set != id_set2:
                ids_to_remove.append(id_set[0])
    return ids_to_remove


class CategoryBundleView(TaskCategoryListViewAlt, SingleObjectMixin):
    model = CategoryBundle

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(CategoryBundle, pk=kwargs['pk'])
        return super(CategoryBundleView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        self.primary_categories = TaskCategory.objects.filter(
            bundles__id=self.object.id)
        self.bundled_categories = []
        cat_ids = [get_descendant_ids(cat) for cat in self.primary_categories]
        duplicates = remove_duplicate_ids(cat_ids)
        print duplicates
        for cat in self.primary_categories[:]:
            if cat.id not in duplicates:
                self.bundled_categories.append(cat)
        print self.bundled_categories
        return self.bundled_categories


class CategoryBundleListView(generic.ListView):
    #TODO: Might include category info here, for now, keeping it light-weight
    model = CategoryBundle

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(CategoryBundleListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.queryset = super(CategoryBundleListView, self).get_queryset()
        context = []
        for bundle in self.get_queryset():
            context.append({
                'id': bundle.id,
                'title': bundle.title,
                'title_url': urlquote(bundle.title),
                #'update_url': bundle.get_update_url(),
                #'order': bundle.order,
            })

        return context


class CategoryBundleFormView(generic.CreateView):
    model = CategoryBundle
    form_class = CategoryBundleForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(CategoryBundleFormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        update_url = form.instance.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html,
                   'pk': form.instance.id}
        return context

    def form_invalid(self, form):
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        form_html = render_crispy_form(self.form_class())
        context = {'form_html': form_html}
        return context


class CategoryBundleUpdateView(generic.UpdateView):
    model = CategoryBundle
    form_class = CategoryBundleForm

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(CategoryBundleUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        update_url = self.object.get_update_url()
        form_html = render_crispy_form(self.form_class())
        context = {'success': True, 'update_url': update_url, 'form_html': form_html}
        return context

    def form_invalid(self, form):
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        return {'success': False, 'form_html': form_html}

    def get(self, request, *args, **kwargs):
        self.object = super(CategoryBundleUpdateView, self).get_object()
        form = self.form_class(instance=self.object)
        form.helper.form_action = self.object.get_update_url()
        form_html = render_crispy_form(form)
        context = {'form_html': form_html}
        return context


class CategoryBundleDeleteView(generic.DeleteView):
    model = CategoryBundle
    success_url = reverse_lazy('tasks:bundle-list')

    @json_view
    def dispatch(self, *args, **kwargs):
        return super(CategoryBundleDeleteView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        #TODO: Form processing needed
        form.save()
        context = {'success': True}
        return context

    def form_invalid(self, form):
        return {'success': False}

    def delete(self, request, *args, **kwargs):
        self.object = super(CategoryBundleDeleteView, self).get_object()
        self.object.delete()
        return {'success':True}
