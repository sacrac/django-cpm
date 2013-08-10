import json

from django.http import HttpResponse
from django.shortcuts import render


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            update_url = False
            if self.object.get_update_url():
                update_url = self.object.get_update_url()
            data = {
                'success': True,
                'pk': self.object.pk,
                'update_url': update_url
                }
            return self.render_to_json_response(data)
        else:
            return response

import urllib

def snippet_list(request):
    json_str = urllib.URLopener().open('http://127.0.0.1:8010/snippets/')
    snippets = json.load(json_str)['results']
    print(snippets)
    return render(request, 'core/snippet_list.html', {'snippet_list': snippets})
