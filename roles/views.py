from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from roles.models import Profile
from roles.forms import ProfileForm
from django.contrib import messages

class ShowProfile(LoginRequiredMixin, DetailView):
    model = Profile

    def get_object(self, queryset=None):
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404("User not found")

    def get_user(self):
        return self.get_object().user

class EditProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "roles/profile_form.html"

    def get(self, *args, **kwargs):
        profile = self.request.user.profile
        form = ProfileForm({
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
        }, profile.user)
        context = {
            'profile': profile,
            'form': form,
            'url': reverse_lazy('roles:edit')
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        profile = self.request.user.profile
        form = ProfileForm(self.request.POST, profile.user)
        if form.is_valid(): 
            profile.user.first_name = form.cleaned_data['first_name']
            profile.user.last_name = form.cleaned_data['last_name']
            profile.user.save()
            return redirect('roles:detail')
        else:
            context = {
                'profile': profile,
                'form': form,
                'url': reverse_lazy('profiles:edit')
            }
            return render(self.request, self.template_name, context)

class ChangePassword(PasswordChangeView):
    template_name = "roles/password_form.html"
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['profile'] = profile
        return context

    def post(self, *args, **kwargs):
        result = super().post(*args, **kwargs)
        if result.status_code == 302:
            messages.info(self.request, "You changed your password.")
        return result

