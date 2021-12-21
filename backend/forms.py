# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.models import *
from backend.models import *
from datetime import date


class SignUpForm(UserCreationForm):
    
    first_name = forms.CharField(
        
        label = 'First Name',
        max_length = 32,
        help_text='*',
        widget=forms.TextInput(
            attrs={'placeholder':'','class':'abc'},
            ),
            
        )

    
    email = forms.EmailField(max_length=254,required=True, help_text='*',widget=forms.TextInput(
            attrs={'placeholder':'','class':''},
            ))

    username = forms.CharField(max_length=254,required=True, help_text='*',widget=forms.TextInput(
            attrs={'placeholder':'','class':''},
            ))
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
    
    class Meta:
        model = User
        exclude=['password','last_login','user_permissions','date_joined']
        fields = ('__all__')

    

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')


class EditUserForm(ModelForm):
    first_name = forms.CharField(
        
        label = 'First Name',
        max_length = 32,
        help_text='*',
        widget=forms.TextInput(
            attrs={'placeholder':'','class':'abc'},
            ),
            
        )

    
    email = forms.EmailField(max_length=254,required=True, help_text='*',widget=forms.TextInput(
            attrs={'placeholder':'','class':''},
            ))

    username = forms.CharField(max_length=254,required=True, help_text='*',widget=forms.TextInput(
            attrs={'placeholder':'','class':''},
            ))
    
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
    
    class Meta:
        model = User
        exclude=['password','last_login','user_permissions','date_joined','password1','password2']
        

    

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

# paypal form...
class UserDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserDetailForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    parent_user = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Regional Manager',is_active=True),required=False)
    class Meta:
        model = ParentUser
        exclude=['current_user']
        fields = ('__all__')

class SMEUserDetailForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SMEUserDetailForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    parent_user = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Concierge Manager',is_active=True),required=False)
    class Meta:
        model = ParentUser
        exclude=['current_user']
        fields = ('__all__')
    
class ManufacturerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ManufacturerForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Manufacturer
        fields = ('__all__')


class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Categories
        fields = '__all__'

class PagesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PagesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Pages
        fields = '__all__'
        ordering = ['-created_date']

class ProductForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Product
        fields = '__all__'
        exclude=['priority_order','Owner']
        ordering = ['-created_date']

class RateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RateForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Credits
        fields = '__all__'
        ordering = ['-created_date']


class AttributeBaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttributeBaseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = AttributeBase
        fields = '__all__'
        ordering = ['-created_date']

class AttributeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttributeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Attribute
        fields = '__all__'
        ordering = ['-created_date']

class ProductAttributeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAttributeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = ProductAttribute
        exclude=['product']
        fields = '__all__'
        ordering = ['-created_date']