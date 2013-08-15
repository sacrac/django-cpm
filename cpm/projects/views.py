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

from core.views import AjaxableResponseMixin
from tasks.models import TaskCategory
from tasks.forms import TaskForm, TaskCategoryForm
from jsonview.decorators import json_view

from .forms import ProjectForm, ProjectFilterForm
from .models import Project, ProjectImage


def unique_items(list):
    unique_list = []
    for item in list:
        if not item in unique_list:
            unique_list.append(item)
    return unique_list


def get_dict_in_list(key, value, dict_list):
    """
    Looks through a list of dictionaries and returns dict, where dict[key] == value
    """
    result = None
    for dict in dict_list:
        if dict[key] == value:
            result = dict
    return result


def get_branch_by_id(tree, id):
    """
    looks through a tree recursively for dict['id'] == id and returns the branch.
    Assumes that each branch item has a key, ['children'], that contains a list of dict objects in the same format as tree
    and another key, ['ascendants'], that is a string of ids starting with the dict object's top-level ancestor's id and
    each other ancestor ending with that dict object's id i.e
    tree =
    [
        {'id': 1,
        'ascendants': "1",
        'children': [
            {'id': 2,
            'ascendants': "1,2",
            'children': [
                {'id': 4,
                'ascendants': "1,2,4",
                'children': [
                    {'id': 5,
                    'ascendants': "1,2,4,5",
                    'children': [ ]
                    }
                }
                {'id': 3,
                'ascendants': "1,2,3",
                'children': [ ]
                }
            }
        },
        {'id': 6,
        'ascendants: "6",
        'children: []
        }
    ]
    """
    for branch in tree:
        if branch['id'] == id:
            print branch['id']
            return branch
        elif branch['children']:
            branch = get_branch_by_id(branch['children'], id)
            if branch:
                return branch


def get_used_branch_ids(p_tree):
    """
    p_tree = p['category_totals']
    returns list of branch ids and all of their ancestor ids, filters redundancies
    *NOTE: this is depending on the 'ascendants' method of task categories. If the 'ascendants' method isnt updating
    correctly, it is likely the cause of any issues with project summaries
    """
    used_object_ids = []
    for branch in p_tree:
        branch_ascendants = p_tree[branch]['ascendants'].split(',')
        branch_ascendants = [int(item) for item in branch_ascendants]
        used_object_ids.extend(branch_ascendants)
    used_object_ids = unique_items(used_object_ids)
    return used_object_ids


def create_used_item_list(tree, used_branch_ids):
    """
    using a list of ids, creates a list of branches with those ids
    NOTE: any modifications to branches should be done here or immediately after
    """
    branches = []
    for id in used_branch_ids:
        print id
        branch = get_branch_by_id(tree, id)
        branches.append(branch)
    for branch in branches:
        branch['children'] = []
    return branches


def modify_used_item_list(p_tree, used_item_list):
    """
    modify list of branches to include additional key, values
    """
    for item in used_item_list:
        task_set = []
        for task in p_tree[str(item['id'])]['task_set']:
            task_set.append(p_tree[str(item['id'])]['task_set'][str(task)])
        item['task_set'] = task_set
        item['expense'] = p_tree[str(item['id'])]['expense']
        item['price'] = p_tree[str(item['id'])]['price']
        item['total'] = p_tree[str(item['id'])]['total']


def add_info_to_branch(tree, id, item):
    """
    adds item (branch) to a branch's children and increases price, expense, total of branch to include items values
    """
    target = None
    for branch in tree:
        if branch['id'] == id:
            target = branch
        elif branch['children']:
            target = get_branch_by_id(branch['children'], id)
    if target:
        target['children'].append(item)
        target['price'] += item['price']
        target['expense'] += item['expense']
        target['total'] += item['total']


def create_used_item_tree(used_item_list):
    """
    takes branches and organizes them into a recursive tree (or whatever this id called??)
    branches are modified with "add_info_to_branch" function
    """
    used_item_tree = []
    for item in used_item_list[:]:
        print str(item['id']) + ' : ' + str(item['parent'])
        if item['parent'] is None:
            print 'primary %d' % item['id']
            used_item_tree.append(item)
            used_item_list.remove(item)
    while len(used_item_list) is not 0:
        for item in used_item_list[:]:
            parent = get_dict_in_list('id', item['parent'], used_item_list)
            if not parent:
                add_info_to_branch(used_item_tree, item['parent'], item)
                used_item_list.remove(item)
                print 'child %d' % item['id']
    return used_item_tree


def create_project_summary_tree(c_url='http://127.0.0.1:8000/cpm/tasks/category/alt/',
                                p_url='http://127.0.0.1:8000/cpm/projects/json/',
                                project_id=1):
    p = json.load(urllib.URLopener().open(p_url + str(project_id) + '/'))['category_totals']
    c = json.load(urllib.URLopener().open(c_url))['category_list']
    used_branch_ids = get_used_branch_ids(p)
    used_item_list = create_used_item_list(c, used_branch_ids)
    modify_used_item_list(p, used_item_list)
    used_item_tree = create_used_item_tree(used_item_list)
    return used_item_tree


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
            'category_totals': self.object.get_project_category_totals()
        }

        return context


class ProjectDetailView(AjaxableResponseMixin, generic.DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        #todo: remove form from this view
        context = {
            'form': TaskForm(),
        }
        context.update(kwargs)
        return super(ProjectDetailView, self).get_context_data(**context)


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
        self.user = get_object_or_404(User, id=self.args[0])
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
        form.save()
        form_html = render_crispy_form(form)
        context = {'success': True, 'form_html': form_html, 'pk': form.instance.id}
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

