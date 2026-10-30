from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
    )
    phone = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': '07XX XXX XXX'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Password'
        })


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }