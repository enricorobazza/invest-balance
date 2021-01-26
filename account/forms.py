from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as UserCreationModelForm
from account.models import User


class UserLoginForm(forms.Form):
    email = forms.CharField()
    email.widget.attrs['class'] = 'form-control'
    email.widget.attrs['placeholder'] = 'Usuário'
    password = forms.CharField(widget=forms.PasswordInput)
    password.widget.attrs['class'] = 'form-control'
    password.widget.attrs['placeholder'] = 'Senha'

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Verifique seu usuário e senha.')
            if not user.is_active:
                raise forms.ValidationError(
                    'Esta conta foi desativada, por favor contate um administrador.')
        return super(UserLoginForm, self).clean(*args, **kwargs)

    # def __init__(self, *args, **kwargs):
    #     fields = self['declared_fields']
    #     username = fields['username']
    #     self['base_fields'].username.widget.attrs['class'] = 'form-control'
    #     self['base_fields'].password.widget.attrs['class'] = 'form-control'


class UserCreationForm(UserCreationModelForm):
    class Meta:
        fields = ('email', 'password1', 'password2')
        model = User

    def __init__(self, *args, **kwargs):
        super(UserCreationModelForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
