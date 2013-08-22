from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Button, Submit
from django import forms
from .models import ChangeOrder


class ChangeOrderForm(forms.ModelForm):
    class Meta:
        model = ChangeOrder
        fields = ['title', 'slug', 'project', 'description']
        widgets = {
            'slug': forms.HiddenInput(),
            'project': forms.HiddenInput(),
            }

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        super(ChangeOrderForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        #self.helper.form_tag = False
        self.helper.form_id = 'change-form'
        self.helper.form_class = 'form-horizontal'
        #self.helper.form_action = 'updates:update-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('title'),
                    'slug',
                    'project'
                ),
                Div(
                    Field('description'),
                    ),
                Div(
                    FormActions(
                        Submit('save_change', 'Submit', css_class="btn-primary"),
                        Button('cancel', 'Cancel')
                    )
                )
            )
        )
