from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.views import generic

from django.utils import timezone
from django.utils.safestring import mark_safe
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout as auth_logout
from .forms import *
import re, json
from django.core.validators import validate_slug

from django.utils.safestring import SafeString

# Create your views here.

# Index
def index(request):
    return render(request, 'editor/index.html')

# Handling errors

def error404(request):
    return render(request, 'editor/errors/404.html')

def error403(request):
    return render(request, 'editor/errors/403.html')

# Post section

class PostIndexView(generic.ListView):
    template_name = 'editor/index.html'
    context_object_name = 'posts'
    model = Post
    paginate_by = 5

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', '')
        if query != '':
            queryDict = json.loads(query)
            collection = Post.objects.filter(keyword__contains="")
            for i in queryDict:
                keyword = i.get('value')
                collection = collection.filter(keyword__contains=keyword)
            return collection.order_by('-pub_date')[:5]
        # get queryset of posts which method was_published_recently is True
        return Post.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        data["query"] = query
        return data

class PostView(FormMixin, generic.DetailView):
    template_name = 'editor/post/read.html'
    model = Post
    form_class = CommentForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        post = self.get_object()
        
        keywords = json.loads(post.keyword)
        keywordsList = list()
        
        for keyword in keywords:
            keywordsList.append(keyword.get('value'))
            
        data["keywords"] = keywordsList
        return data

class PostCommentsView(generic.DetailView):
    template_name = 'editor/comment/list.html'
    model = Post

class PostCreateView(PermissionRequiredMixin , LoginRequiredMixin, generic.CreateView):
    permission_required = ["editor.add_post", "is_staff"]
    template_name = 'editor/post/create.html'
    form_class = PostForm
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    success_url = '/post/create'
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, mark_safe('Post created successfully. <a href="%s">View it</a>'%reverse('editor:post.view', kwargs={'slug': post.slug})))
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'editor/post/update.html'
    form_class = PostForm
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    model = Post
    success_url = '/post/update/'
    
    def get_success_url(self) -> str:
        return reverse('editor:post.view', kwargs={'slug': self.object.slug})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.success(self.request, mark_safe('Post updated successfully. <a href="%s">View it</a>'%reverse('editor:post.view', kwargs={'slug': post.slug})))
        return super().form_valid(form)
    
class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = 'editor/post/delete.html'
    model = Post
    success_url = '/post/create'
    login_url = '/login/'
    redirect_field_name = 'redirected_to'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, mark_safe('Post deleted successfully. '))
        return super().form_valid(form)


# For comments
    
class CommentCreate(LoginRequiredMixin, generic.CreateView):
    template_name = ''
    form_class = CommentForm
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    success_url = '/post/'

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return HttpResponseRedirect(reverse('editor:post.view', kwargs={'slug': self.kwargs["slug"]}))

    def get_success_url(self) -> str:
        return reverse('editor:post.view', kwargs={'slug': self.kwargs["slug"]})
    

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.post = Post.objects.get(slug=self.kwargs["slug"])
        comment.save()
        messages.success(self.request, mark_safe('Comment submitted successfully.'))
        return super().form_valid(form)
    
class CommentDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = ''
    form_class = CommentForm
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    success_url = '/post/'

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            comment = Comment.objects.get(id=self.kwargs["pk"])
            if comment.user == self.request.user:
                comment.delete()
                messages.success(self.request, mark_safe('Comment deleted successfully.'))
            else:
                messages.error(self.request, mark_safe('You can only delete your own comments.'))
        except:
            # if comment not found
            messages.error(self.request, mark_safe('Comment not found.'))
        
        return HttpResponseRedirect(reverse('editor:post.view', kwargs={'slug': self.kwargs["slug"]}))

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
    
class UserProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    login_url = '/login/'
    redirect_field_name = 'redirected_to'
    template_name = "editor/user/update.html"
    model = User
    form_class = UserForm
    success_url = '/user/profile/update'

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.user
    
    def get_queryset(self):
        return self.request.user
    
    def form_valid(self, form: UserForm) -> HttpResponse:

        if self.request.GET.get('type') == 'password':
            form.cleaned_data['email'] = self.request.user.email
            user = form.save(commit=False)

            # User failed to authenticate
            if not authenticate(username=self.request.user.username, password=form.cleaned_data['curr_password']):
                form.add_error(field="curr_password", error="Wrong current password")
                return super().form_invalid(form)

            # Password and confirm password do not match
            if form.cleaned_data['password'] != form.cleaned_data['c_password']:
                form.add_error(field="c_password", error="New password and confirm new password fields do not match")
                return super().form_invalid(form)

            # If everything works
            user.set_password(form.cleaned_data['password'])
            login(self.request, user)
            # Success message
            messages.success(self.request, mark_safe('Information updated successfully'))
            user.save()
        else:
            user = form.save(commit=False)

            # User failed to authenticate
            if not authenticate(username=self.request.user.username, password=form.cleaned_data['curr_password']):
                form.add_error(field="curr_password", error="Wrong current password")
                return super().form_invalid(form)
            
            # Success message
            messages.success(self.request, mark_safe('Information updated successfully'))
            user.save()

        return super().form_valid(form)
    
# Chat section
    
def chat(request):
    return render(request, 'editor/chat/index.html')

def room(request, room_name):
    return render(request, "editor/chat/room.html", {"room_name": room_name})