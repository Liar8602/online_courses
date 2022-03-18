from django import forms
from django.contrib.auth.models import User

from .models import StudentProfile, CourseRegistration


class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields= ('username', 'email', 'password')


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('category',)


class CourseRegistrationForm(forms.ModelForm):
    class Meta:
        model = CourseRegistration
        fields = ('course', 'student')