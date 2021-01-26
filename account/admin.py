from django.contrib import admin
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.

from account.models import User

class UserCreationForm(forms.ModelForm):
  password1 = forms.CharField(label="Password", widget = forms.PasswordInput)
  password2 = forms.CharField(label="Password Confirmation", widget = forms.PasswordInput)

  class Meta:
    model = User
    fields = ('email', )

  def clean_password2(self):
    password1 = self.cleaned_data.get("password1")
    password2 = self.cleaned_data.get("password2")
    if(password1 and password2 and password1 != password2):
      raise forms.ValidationError("Passwords don't match")
    return password2


class UserChangeForm(forms.ModelForm):
  password = ReadOnlyPasswordHashField()

  class Meta:
    model = User
    fields = ('email','password', 'is_active', 'is_admin', 'is_superuser')

  def clean_password(self):
    return self.initial["password"]

class UserAdmin(BaseUserAdmin):
  form = UserChangeForm
  add_form = UserCreationForm

  list_display = ('email', 'is_active', 'is_admin', 'is_superuser', 'is_premium', 'date_joined')
  list_filter = ('is_admin', )
  fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Permissions', {'fields': ('is_admin', 'is_superuser', 'is_active')}),
    ('Premium', {'fields': ('is_premium', )}),
    ('Dates', {'fields': ('date_joined', )})
  )

  add_fieldsets = (
    (None, {
      'classes': ('wide'),
      'fields': ('email', 'password1', 'password2')
    }),
  )

  search_fields = ('email', )
  ordering = ('email', )
  filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)

