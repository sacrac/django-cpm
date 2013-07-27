from django import forms
from django.utils.safestring import mark_safe


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    From: Mezzanine, @stephenmcd
    Wraps render with a CSS class for styling.
    """
    def render(self, *args, **kwargs):
        rendered = super(CheckboxSelectMultiple, self).render(*args, **kwargs)
        return mark_safe("<span class='multicheckbox'>%s</span>" % rendered)

