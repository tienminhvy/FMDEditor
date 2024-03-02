from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from django.utils import timezone
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from .forms import *

# Create your views here.

# Index
def index(request):
    return render(request, 'editor/index.html')

# Post section

class PostIndexView(generic.ListView):
    template_name = 'editor/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # get queryset of posts which method was_published_recently is True
        return Post.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    
class PostView(generic.DetailView):
    template_name = 'editor/detail.html'
    model = Post

# For login

class LoginView(generic.FormView):
    template_name = 'editor/login.html'
    success_url = '/'
    form_class = LoginForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        # Check authentication
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password']);
        if user is not None:
            login(self.request, user)
            # If user get redirect to login page from another page
            if self.request.GET.get('redirected_to'):
                return HttpResponseRedirect(self.request.GET.get('redirected_to'))
            # else
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(self.request, self.template_name, {'form': form, 'error': 'Invalid username or password'})
        
    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'error': 'Something went wrong!'})

# For register

class RegisterView(generic.FormView):
    template_name = 'editor/register.html'
    success_url = '/'
    form_class = RegisterForm
    
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        
        # Check for error
        error = ""
        if User.objects.filter(username=form.cleaned_data['username']).exists():
            error += "Username %s already exists" % form.cleaned_data['username']
        if User.objects.filter(username=form.cleaned_data['email']).exists():
            error += "\nEmail %s already exists" % form.cleaned_data['email']

        # Error(s) found
        if (len(error) > 0):
            return render(self.request, self.template_name, {'form': form, 'error': error})
        
        # Else
        user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
        try:
            user.save()
            return render(self.request, self.template_name, {'form': form, 'success': "Account created successfully. Now you can login with your provided credentials."}) 
        except:
            return render(self.request, self.template_name, {'form': form, 'error': "Something went wrong on our code/server!"})

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'error': 'Something went wrong!'})

# For logout

def logout(request):
    auth_logout(request)
    return render(request, 'editor/logout.html')

# For user profile view

class UserProfileView(LoginRequiredMixin, generic.TemplateView):
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    template_name = "editor/user/profile.html"
    
    def get_queryset(self):
        return self.request.user