from django import forms
from projects.models import Project

from .models import Update


class UpdateWizardForm1(forms.ModelForm):
    class Meta:
        model = Update
        exclude = ('project',)


class UpdateWizardForm2(forms.Form):
    task_set = forms.CheckboxSelectMultiple()