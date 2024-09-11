from django import forms
from django.contrib.auth.forms import UserChangeForm
from recipes.models import Tag
from user.models import User


class TagForm(forms.ModelForm):

    class Meta:
        model = Tag
        fields = (
            'name',
            'slug',
        )
        widgets = {
            'name': forms.TextInput,
            'slug': forms.TextInput,
        }


class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
