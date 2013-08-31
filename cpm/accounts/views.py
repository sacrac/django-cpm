from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.messages import info, error
from django.contrib.auth.decorators import login_required
from django.views import generic

from .forms import UserCreationForm


def signup(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid:
            info(request, 'Successfully signed up')
            new_user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get("next"))
    return render(request, 'accounts/signup.html', {'form': form})



@login_required
def profile(request, id):
    lookup = {"id__iexact": id, "is_active": True}
    context = {"profile_user": get_object_or_404(User, **lookup)}
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_redirect(request):
    """
    Just gives the URL prefix for profiles an action - redirect
    to the logged in user's profile.
    """
    return redirect("accounts:profile", id=request.user.id)


class UserListView(generic.ListView):
    model = User
