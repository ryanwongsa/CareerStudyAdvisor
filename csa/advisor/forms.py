from django import forms
from models import UserProfile, Category
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

'''
    Registration form, to create an account for the user
'''
class MyRegistrationForm(UserCreationForm):
    
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = {'username', 'email', 'password1', 'password2'}
    
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save(commit=False)
        
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user

'''
    Form that allows the user to update their profile
'''
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields={'interests','subjects'};

   