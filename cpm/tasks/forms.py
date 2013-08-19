from crispy_forms.bootstrap import FormActions
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import PrependedText
from django.forms.extras.widgets import SelectDateWidget

from .models import Task, TaskCategory


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'slug', 'description', 'project', 'expense', 'price',
                  'category']
        widgets = {
            'slug': forms.HiddenInput(),
            #'projected_completion_date': SelectDateWidget(),
            'completion_date': forms.HiddenInput(),
            'project': forms.HiddenInput(),
            'changes': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'task-form'
        #self.helper.form_class = 'span4'
        #self.helper.form_action = 'tasks:task-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    'slug',
                    Field('title', css_class="input-block-level"),
                    Field('category', css_class="input-block-level"),
                    Div(
                        Field('expense', wrapper_class='span2', css_class='input-small'),
                        Field('price', wrapper_class='span2', css_class='input-small'),
                        css_class='controls controls-row row',
                    )
                    #'projected_completion_date',
                ),
                Div(
                    Field('description', rows=3, css_class='input-block-level'),
                ),
                Div(
                    'project',
                    'changes',
                    FormActions(
                        Submit('save_task', 'Save Task', css_class="btn-primary"),
                        Button('cancel', 'Cancel'),
                        Button('delete', 'Delete')
                        )
                )
            )
        )


class TaskCategoryForm(forms.ModelForm):
    class Meta:
        model = TaskCategory
        fields = ['title', 'order', 'description', 'parent']
        widgets = {
            'order': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(TaskCategoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'task-category-form'
        #self.helper.form_class = 'span4'
        #self.helper.form_action = 'tasks:task-category-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('title', css_class="input-block-level"),
                    Field('parent', css_class="input-block-level"),
                    Field('description', rows=3, css_class='input-block-level'),
                    'order'
                ),
                Div(
                    FormActions(
                        Submit('submit', 'Submit', css_class="btn-primary"),
                        Button('cancel', 'Cancel')
                    )
                )
            )
        )


