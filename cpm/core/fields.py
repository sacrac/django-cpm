from django.utils.importlib import import_module

__author__ = 'wpl'
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.forms import MultipleChoiceField
from django.utils.text import capfirst

from .utils import import_dotted_path



class MultiChoiceField(models.CharField):
    """
    From: Mezzanine, @stephenmcd
    Charfield that stores multiple choices selected as a comma
    separated string. Based on http://djangosnippets.org/snippets/2753/
    """

    __metaclass__ = models.SubfieldBase  # triggers to_python()

    def formfield(self, *args, **kwargs):
        from .forms import CheckboxSelectMultiple
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "choices": self.choices,
            "widget": CheckboxSelectMultiple,
            "initial": self.get_default() if self.has_default() else None,
        }
        defaults.update(kwargs)
        return MultipleChoiceField(**defaults)

    def get_db_prep_value(self, value, **kwargs):
        if isinstance(value, (tuple, list)):
            value = ",".join([unicode(i) for i in value])
        return value

    def to_python(self, value):
        if isinstance(value, basestring):
            value = value.split(",")
        return value

    def validate(self, value, instance):
        choices = [unicode(choice[0]) for choice in self.choices]
        if set(value) - set(choices):
            error = self.error_messages["invalid_choice"] % value
            raise ValidationError(error)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return ",".join(value)


class FileField(models.FileField):
    def __init__(self, *args, **kwargs):
        for fb_arg in ("format", "extensions"):
            kwargs.pop(fb_arg, None)
        super(FileField, self).__init__(*args, **kwargs)

