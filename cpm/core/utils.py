from django.utils.importlib import import_module

__author__ = 'wpl'



def import_dotted_path(path):
    """
    From: Mezzanine, @stephenmcd
    Takes a dotted path to a member name in a module, and returns
    the member after importing it.
    """
    try:
        module_path, member_name = path.rsplit(".", 1)
        module = import_module(module_path)
        return getattr(module, member_name)
    except (ValueError, ImportError, AttributeError), e:
        raise ImportError("Could not import the name: %s: %s" % (path, e))


