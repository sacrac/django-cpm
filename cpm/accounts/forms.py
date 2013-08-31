from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm




user = get_user_model()

class UserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.help_text_inline = True
        self.helper.form_tag = False
        #self.helper.form_id = 'authentication-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(
                Field('username'),
                Field('password1'),
                Field('password2'),
                Field('email'),
                Field('first_name'),
                Field('last_name')
            ),
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


