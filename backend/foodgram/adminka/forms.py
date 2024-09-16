from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model

from recipes.models import Tag

User = get_user_model()


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
