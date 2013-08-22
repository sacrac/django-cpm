from crispy_forms.bootstrap import FormActions
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.forms.extras.widgets import SelectDateWidget

from .models import Project, ProjectImage


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['user', 'title', 'slug', 'description', 'start_time', 'completion']
        widgets = {
            'slug': forms.HiddenInput(),
            'completion': forms.HiddenInput(),
            'start_time': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'project-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = 'projects:project-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    'slug',
                    Field('user'),
                    Field('title'),
                    Field('start_time'),
                ),
                Div(
                    Field('description'),
                ),
                Div(
                    FormActions(
                        Submit('save_project', 'Submit', css_class="btn-primary"),
                        Button('cancel', 'Cancel')
                    )
                )
            )
        )


class ProjectFilterForm(forms.Form):
    date = forms.DateField(widget=SelectDateWidget(), label='Month')

    def __init__(self, *args, **kwargs):
        super(ProjectFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('date'),
                css_class='pull-left'

            )

        )


class ProjectImageForm(forms.ModelForm):
    model = ProjectImage

    class Meta:
        model = ProjectImage
        fields = ['title', 'slug', 'project', 'update', 'change_order', 'image']
        widgets = {
            'slug': forms.HiddenInput(),
            'project': forms.HiddenInput(),
            'update': forms.HiddenInput(),
            'change_order': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectImageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'project-image-form'
        self.helper.form_class = 'form-inline'
        #self.helper.form_action = 'projects:project-form'
        self.helper.layout = Layout(
            Div(
                'slug',
                'project',
                'update',
                'change_order',
                Field('title'),
                Field('image'),
                Submit('save_project_image', 'Submit', css_class="btn-primary"),
                Button('cancel', 'Cancel')
            )
        )
