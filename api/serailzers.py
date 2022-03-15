from rest_framework import serializers

from django.contrib.auth.models import User
from courses.models import StudentProfile


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = StudentProfile
        fields = '__all__'