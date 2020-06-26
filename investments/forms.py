from django import forms
from django.contrib.auth import authenticate
from .models import Asset, Category, AssetPurchase, Transfer, Saving

class UserLoginForm(forms.Form):
    username = forms.CharField()
    username.widget.attrs['class'] = 'form-control'
    username.widget.attrs['placeholder'] = 'Usuário'
    password = forms.CharField(widget=forms.PasswordInput)
    password.widget.attrs['class'] = 'form-control'
    password.widget.attrs['placeholder'] = 'Senha'

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Verifique seu usuário e senha.')
            if not user.is_active:
                raise forms.ValidationError(
                    'Esta conta foi desativada, por favor contate um administrador.')
        return super(UserLoginForm, self).clean(*args, **kwargs)

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ('stock_exchange', 'category', 'name', 'short_code', 'code', 'user', 'score')

    def __init__(self, user, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['category'].queryset = Category.objects.filter(user=user, type=1)
        self.fields['name'].widget.attrs['placeholder'] = "Ex: Ambev"
        self.fields['short_code'].widget.attrs['placeholder'] = "Ex: ABEV3"
        self.fields['code'].widget.attrs['placeholder'] = "Ex: ABEV3.SA"
        self.fields['score'].widget.attrs['placeholder'] = "Ex: 6,5"

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('title', 'weight', 'user', 'type')

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['placeholder'] = "Ex: Ações Brasileiras"
        self.fields['weight'].widget.attrs['placeholder'] = "Ex: 2"


class AssetPurchaseForm(forms.ModelForm):
    class Meta:
        model = AssetPurchase
        fields = ('asset', 'date', 'value', 'amount', 'transfer', 'taxes_value')

    def __init__(self, user, *args, **kwargs):
        super(AssetPurchaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['asset'].queryset = Asset.objects.filter(user=user)
        self.fields['transfer'].queryset = Transfer.objects.filter(user=user).order_by('-date')
        self.fields['date'].widget.attrs['class'] += ' datepicker'
        self.fields['value'].widget.attrs['placeholder'] = "Ex: 11,53"
        self.fields['amount'].widget.attrs['placeholder'] = "Ex: 5"
        self.fields['taxes_value'].widget.attrs['placeholder'] = "Ex: 1,00"
        self.fields['taxes_value'].widget.attrs['required'] = False

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ('from_currency', 'to_currency', 'value', 'final_value', 'date', 'user')

    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['class'] += ' datepicker'

class SavingForm(forms.ModelForm):
    class Meta:
        model = Saving
        fields = ('bank', 'amount', 'final_amount', 'date', 'category', 'user')

    def __init__(self, user, *args, **kwargs):
        super(SavingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['class'] += ' datepicker'
        self.fields['category'].queryset = Category.objects.filter(user=user, type=2)