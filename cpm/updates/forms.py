from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Button
from django import forms
from projects.models import Project

from .models import Update


class UpdateWizardForm1(forms.ModelForm):
    class Meta:
        model = Update
        exclude = ('project',)


class UpdateWizardForm2(forms.Form):
    task_set = forms.CheckboxSelectMultiple()

class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ['title', 'slug', 'project', 'description', 'tasks']
        widgets = {
            'slug': forms.HiddenInput(),
            'project': forms.HiddenInput(),
            }

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'update-form'
        self.helper.form_class = 'form-horizontal'
        #self.helper.form_action = 'updates:update-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('title'),
                    'slug',
                    'project',
                    'tasks'
                    ),
                Div(
                    Field('description'),
                    ),
                Div(
                    FormActions(
                        Submit('save_update', 'Submit', css_class="btn-primary"),
                        Button('cancel', 'Cancel')
                    )
                )
            )
        )
